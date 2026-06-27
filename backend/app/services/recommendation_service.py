from app.services.data_loader import find_by_title

def enrich_recommendations(llm_recs: list[dict], disliked_movies: list[str] = None) -> list[dict]:
    """
    Cross-references LLM recommendations against movies.csv.
    Enriches with: genre, rating, year, overview.
    Appends the LLM's 'justification' as the reason on the movie card.
    Filters out any recommendation that doesn't match a catalog item.
    Also serves as a safety filter to ensure no movie from the session's
    disliked list is recommended.
    """
    enriched_cards = []
    seen_titles = set()
    
    # Normalize disliked movies for easy comparison
    disliked_normalized = {d.strip().lower() for d in disliked_movies} if disliked_movies else set()
    
    for rec in llm_recs:
        proposed_title = rec.get("title")
        justification = rec.get("justification")
        
        if not proposed_title:
            continue
            
        # Query movies.csv via fuzzy matching data loader
        movie_data = find_by_title(proposed_title)
        if movie_data:
            movie_title = movie_data["title"]
            movie_title_lower = movie_title.lower()
            
            # Double-check: Filter out if it matches a disliked title
            if movie_title_lower in disliked_normalized:
                continue
                
            # Avoid duplicate recommendations in the same list
            if movie_title not in seen_titles:
                seen_titles.add(movie_title)
                
                enriched_cards.append({
                    "title": movie_title,
                    "genre": movie_data.get("genre"),
                    "rating": float(movie_data.get("rating", 0.0)),
                    "year": int(movie_data.get("year", 0)),
                    "overview": movie_data.get("overview"),
                    "justification": justification
                })
                
    return enriched_cards
