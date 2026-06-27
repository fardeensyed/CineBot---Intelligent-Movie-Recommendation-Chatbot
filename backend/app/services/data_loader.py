import os
import re
import pandas as pd
from rapidfuzz import process, fuzz

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "movies.csv")

# Load the DataFrame once at startup
if os.path.exists(CSV_PATH):
    _df = pd.read_csv(CSV_PATH)
else:
    print(f"Warning: movies.csv not found at {CSV_PATH}. Creating an empty DataFrame.")
    _df = pd.DataFrame(columns=["title", "genre", "rating", "year", "overview"])

def get_df() -> pd.DataFrame:
    """Returns the loaded movies DataFrame."""
    return _df

def search_by_genre(genre: str) -> list[dict]:
    """Search for movies matching a specific genre (case-insensitive substring match)."""
    if _df.empty:
        return []
    # e.g., 'Action' will match 'Action, Sci-Fi'
    filtered = _df[_df['genre'].str.contains(genre, case=False, na=False)]
    return filtered.to_dict(orient='records')

def search_by_min_rating(min_rating: float) -> list[dict]:
    """Search for movies with rating greater than or equal to min_rating."""
    if _df.empty:
        return []
    filtered = _df[_df['rating'] >= min_rating]
    # Sort by rating descending for better recommendations
    filtered = filtered.sort_values(by='rating', ascending=False)
    return filtered.to_dict(orient='records')

def find_by_title(title: str) -> dict | None:
    """
    Find a movie by title using fuzzy matching.
    Handles extra trailing years (e.g. 'Inception (2010)') and minor typos.
    """
    if _df.empty or not title:
        return None
    
    # Strip any trailing year in parenthesis, e.g. "The Matrix (1999)" -> "The Matrix"
    clean_title = re.sub(r'\s*\(\d{4}\)\s*$', '', title).strip()
    clean_title_lower = clean_title.lower()
    
    # First, try an exact case-insensitive match
    exact_match = _df[_df['title'].str.lower() == clean_title_lower]
    if not exact_match.empty:
        return exact_match.iloc[0].to_dict()
        
    # Second, try fuzzy matching using rapidfuzz token_sort_ratio (much safer than WRatio to avoid false positives)
    titles_list = _df['title'].tolist()
    match = process.extractOne(clean_title, titles_list, scorer=fuzz.token_sort_ratio)
    if match:
        best_title, score, index = match
        # A score of 75 or above indicates a good match for sorted tokens
        if score >= 75:
            return _df.iloc[index].to_dict()
            
    # Third, fallback to substring check with word boundaries to avoid false matches (e.g. 'Her' matching inside 'Step Brothers')
    for _, row in _df.iterrows():
        row_title_lower = str(row['title']).lower()
        if clean_title_lower in row_title_lower:
            return row.to_dict()
        if len(row_title_lower) >= 3:
            if re.search(rf"\b{re.escape(row_title_lower)}\b", clean_title_lower):
                return row.to_dict()
            
    return None
