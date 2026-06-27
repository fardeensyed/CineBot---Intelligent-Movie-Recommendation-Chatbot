import sys
import os

# Add backend directory to sys.path to allow imports from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from app.langchain_pipeline.preference_chain import run_preference_extraction
from app.langchain_pipeline.recommend_chain import run_recommendation_generation
from app.langchain_pipeline.phrasing_chain import run_response_phrasing

def test_pipeline():
    print("=== Testing CineBot LangChain Pipeline ===")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("\n[WARNING] GROQ_API_KEY is not set in environment or .env file.")
        print("Please configure your GROQ_API_KEY to run live pipeline tests.")
        print("Skipping LLM calls but imports are verified successfully.")
        return
        
    print("\n--- Test 1: Preference Extraction ---")
    utterance_1 = "I want a funny movie for a lazy Sunday evening"
    print(f"Utterance: '{utterance_1}'")
    prefs_1 = run_preference_extraction(utterance_1, history="")
    print("Extracted Preferences:")
    print(prefs_1)
    
    utterance_2 = "recommend a thriller with rating above 8"
    print(f"\nUtterance: '{utterance_2}'")
    prefs_2 = run_preference_extraction(utterance_2, history="")
    print("Extracted Preferences:")
    print(prefs_2)

    print("\n--- Test 2: Recommendation Generation ---")
    # Feed mock preferences with feedback history
    mock_prefs = {
        "mood": "dark",
        "genre": "Sci-Fi",
        "rating_threshold": 8.0,
        "sentiment_keywords": ["mind-bending", "dark atmosphere"]
    }
    liked = ["Inception"]
    disliked = ["The Matrix Reloaded"]
    
    print("Mock Preferences:", mock_prefs)
    print("Liked:", liked)
    print("Disliked:", disliked)
    
    recs = run_recommendation_generation(mock_prefs, liked_movies=liked, disliked_movies=disliked)
    print("\nGenerated Recommendations:")
    for idx, rec in enumerate(recs, 1):
        print(f"  {idx}. {rec.get('title')} - Justification: {rec.get('justification')}")
        
    print("\n--- Test 3: Response Phrasing ---")
    mock_matched = [
        {
            "title": "Interstellar",
            "genre": "Adventure, Drama, Sci-Fi",
            "rating": 8.6,
            "year": 2014,
            "overview": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."
        }
    ]
    phrased = run_response_phrasing("something like interstellar but darker", mock_matched)
    print("Phrased Response:")
    print(phrased)
    
if __name__ == "__main__":
    test_pipeline()
