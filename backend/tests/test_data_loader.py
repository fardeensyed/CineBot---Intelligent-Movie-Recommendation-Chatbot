import sys
import os

# Add backend directory to sys.path to allow imports from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.data_loader import get_df, search_by_genre, search_by_min_rating, find_by_title

def run_tests():
    print("=== Testing CineBot Data Loader ===")
    
    # 1. Test baseline loading
    df = get_df()
    print(f"DataFrame loaded successfully. Total rows: {len(df)}")
    print("Columns:", list(df.columns))
    assert not df.empty, "DataFrame should not be empty!"
    
    # 2. Test search_by_genre
    action_movies = search_by_genre("Action")
    print(f"\nFound {len(action_movies)} Action movies.")
    if action_movies:
        print("Sample Action Movie:")
        print(f"  Title: {action_movies[0]['title']}")
        print(f"  Genre: {action_movies[0]['genre']}")
        print(f"  Rating: {action_movies[0]['rating']}")
    
    # 3. Test search_by_min_rating
    high_rated = search_by_min_rating(9.0)
    print(f"\nFound {len(high_rated)} movies with rating >= 9.0.")
    for movie in high_rated:
        print(f"  - {movie['title']} ({movie['rating']})")
        
    # 4. Test find_by_title
    print("\nTesting fuzzy title matching...")
    test_titles = [
        "Inception",
        "inception (2010)",  # with year
        "dark knight",        # case-insensitive, partial
        "pulp fiction",      # case-insensitive
        "the godfather"      # prefix/suffix check
    ]
    
    for title in test_titles:
        match = find_by_title(title)
        if match:
            print(f"  Query: '{title}' -> Found: '{match['title']}' (Rating: {match['rating']}, Year: {match['year']})")
        else:
            print(f"  Query: '{title}' -> NOT FOUND")

if __name__ == "__main__":
    run_tests()
