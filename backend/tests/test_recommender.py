import sys
import os

# Add backend directory to sys.path to allow imports from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.recommendation_service import enrich_recommendations

def test_fuzzy_match_hits():
    print("Testing fuzzy match hits...")
    
    # Mock LLM recommendations where some are in the dataset
    llm_recs = [
        {"title": "Inception", "justification": "Matches your preference for high-rated sci-fi."},
        {"title": "pulp fiction", "justification": "Matches your preference for dark drama."}
    ]
    
    enriched = enrich_recommendations(llm_recs)
    print(f"  Enriched count: {len(enriched)}")
    assert len(enriched) == 2, "Both movies should match and be enriched!"
    
    # Check that they have metadata from the CSV
    assert enriched[0]["title"] == "Inception"
    assert enriched[0]["rating"] == 8.8
    assert enriched[0]["justification"] == "Matches your preference for high-rated sci-fi."
    
    assert enriched[1]["title"] == "Pulp Fiction"
    assert enriched[1]["rating"] == 8.9
    print("  test_fuzzy_match_hits passed successfully!")

def test_fuzzy_match_misses():
    print("\nTesting fuzzy match misses...")
    
    # Mock LLM recommendations where some are NOT in the dataset
    llm_recs = [
        {"title": "Inception", "justification": "Matches your preference for high-rated sci-fi."},
        {"title": "Step Brothers", "justification": "A silly comedy movie not in the top 1000."},
        {"title": "Superbad", "justification": "A high school comedy not in the top 1000."}
    ]
    
    enriched = enrich_recommendations(llm_recs)
    print(f"  Enriched count: {len(enriched)}")
    # Step Brothers and Superbad should be dropped because they are not in the CSV
    assert len(enriched) == 1, "Only Inception should match and be enriched!"
    assert enriched[0]["title"] == "Inception"
    print("  test_fuzzy_match_misses passed successfully!")

def test_feedback_exclusion():
    print("\nTesting feedback exclusion...")
    
    # Mock LLM recommendations
    llm_recs = [
        {"title": "Inception", "justification": "Matches your preference for high-rated sci-fi."},
        {"title": "The Dark Knight", "justification": "Matches your preference for gripping thrillers."}
    ]
    
    # Scenario: User has disliked "The Dark Knight" in their session feedback
    disliked = ["The Dark Knight"]
    
    enriched = enrich_recommendations(llm_recs, disliked_movies=disliked)
    print(f"  Enriched count: {len(enriched)}")
    
    # The Dark Knight must be dropped because it is in the disliked list
    assert len(enriched) == 1, "Only Inception should be returned, The Dark Knight should be filtered out!"
    assert enriched[0]["title"] == "Inception"
    
    # Test case-insensitivity in disliked check
    disliked_caps = ["THE DARK KNIGHT"]
    enriched_caps = enrich_recommendations(llm_recs, disliked_movies=disliked_caps)
    assert len(enriched_caps) == 1, "Case-insensitive disliked match should filter it out too!"
    
    print("  test_feedback_exclusion passed successfully!")

if __name__ == "__main__":
    print("=== Running CineBot Recommendation Service Unit Tests ===")
    test_fuzzy_match_hits()
    test_fuzzy_match_misses()
    test_feedback_exclusion()
    print("\n=== All Unit Tests Passed Successfully! ===")
