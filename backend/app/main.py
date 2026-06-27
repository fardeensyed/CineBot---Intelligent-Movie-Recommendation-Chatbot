from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.data_loader import get_df
from app.services.feedback_service import get_feedback, add_feedback
from app.services.recommendation_service import enrich_recommendations
from app.langchain_pipeline.memory import get_memory
from app.langchain_pipeline.preference_chain import run_preference_extraction
from app.langchain_pipeline.recommend_chain import run_recommendation_generation
from app.langchain_pipeline.phrasing_chain import run_response_phrasing

app = FastAPI(
    title="CineBot API",
    description="Backend API for CineBot - Intelligent Movie Recommendation Chatbot",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier for memory and feedback tracking")
    message: str = Field(..., description="User message in natural language")

class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    movie_title: str = Field(..., description="The title of the recommended movie")
    liked: bool = Field(..., description="True if thumbs up, False if thumbs down")

@app.get("/health")
def health_check():
    """Uptime health check endpoint."""
    return {"status": "healthy", "service": "CineBot API"}

@app.get("/movies/search")
def search_movies(
    genre: str = Query(None, description="Filter movies by genre (case-insensitive substring)"),
    min_rating: float = Query(None, description="Filter movies by minimum rating")
):
    """
    Search movies in the dataset directly.
    """
    df = get_df()
    if df.empty:
        return []
        
    filtered = df.copy()
    if genre:
        filtered = filtered[filtered['genre'].str.contains(genre, case=False, na=False)]
    if min_rating is not None:
        filtered = filtered[filtered['rating'] >= min_rating]
        
    filtered = filtered.sort_values(by='rating', ascending=False)
    return filtered.head(20).to_dict(orient='records')

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    Core chatbot endpoint.
    Extracts preferences -> Generates recommendations -> Cross-references database -> Wraps with phrasing.
    """
    session_id = request.session_id
    message = request.message
    
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        # 1. Retrieve memory & conversation history
        memory = get_memory(session_id)
        history_vars = memory.load_memory_variables({})
        history_val = history_vars.get("history", "")
        
        # Format memory if list
        if isinstance(history_val, list):
            history_str = "\n".join([f"{msg.type}: {msg.content}" for msg in history_val])
        else:
            history_str = str(history_val)

        # 2. Retrieve session feedback history
        feedback = get_feedback(session_id)
        liked_movies = feedback.get("liked", [])
        disliked_movies = feedback.get("disliked", [])

        # 3. Step A: Run preference extraction
        preferences = run_preference_extraction(message, history_str)

        # 4. Step B: Generate raw recommendations via Groq
        raw_recs = run_recommendation_generation(
            preferences=preferences,
            liked_movies=liked_movies,
            disliked_movies=disliked_movies
        )

        # 5. Step C: Cross-reference CSV database to enrich metadata
        movie_cards = enrich_recommendations(raw_recs, disliked_movies)

        # 6. Step D: Generate short friendly response phrasing
        if movie_cards:
            reply = run_response_phrasing(message, movie_cards)
        else:
            # Fallback if no matching movies in database
            reply = (
                "I searched the catalog but couldn't find any exact matches for those preferences. "
                "Could you try recommending something else, or adjusting the genre or mood?"
            )

        # 7. Save to conversation memory
        memory.save_context({"input": message}, {"output": reply})

        return {
            "reply": reply,
            "movie_cards": movie_cards
        }

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        # Return generic error details safely
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.post("/feedback")
def feedback_endpoint(request: FeedbackRequest):
    """
    Accepts feedback (thumbs up / thumbs down) for a specific movie recommendation.
    """
    session_id = request.session_id
    movie_title = request.movie_title
    liked = request.liked
    
    try:
        updated_history = add_feedback(session_id, movie_title, liked)
        return {
            "status": "success",
            "message": f"Feedback registered for '{movie_title}'",
            "feedback": updated_history
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record feedback: {str(e)}"
        )
