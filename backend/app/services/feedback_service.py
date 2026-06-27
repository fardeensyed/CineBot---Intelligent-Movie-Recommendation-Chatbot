# In-memory store for user feedback per session
# Format: session_id -> { "liked": [titles], "disliked": [titles] }
# NOTE: For production, this should be backed by a persistent database (e.g. PostgreSQL or Redis).
_feedback_store = {}

def get_feedback(session_id: str) -> dict:
    """
    Get the feedback history (liked and disliked movies) for a session.
    """
    if session_id not in _feedback_store:
        _feedback_store[session_id] = {
            "liked": [],
            "disliked": []
        }
    return _feedback_store[session_id]

def add_feedback(session_id: str, movie_title: str, liked: bool) -> dict:
    """
    Add a movie to the liked or disliked list for a session.
    Removes it from the opposite list if it was previously there.
    """
    history = get_feedback(session_id)
    title_clean = movie_title.strip()
    
    if liked:
        # Add to liked, remove from disliked
        if title_clean not in history["liked"]:
            history["liked"].append(title_clean)
        if title_clean in history["disliked"]:
            history["disliked"].remove(title_clean)
    else:
        # Add to disliked, remove from liked
        if title_clean not in history["disliked"]:
            history["disliked"].append(title_clean)
        if title_clean in history["liked"]:
            history["liked"].remove(title_clean)
            
    return history

def clear_feedback(session_id: str) -> None:
    """Clear feedback history for a session."""
    if session_id in _feedback_store:
        _feedback_store[session_id] = {
            "liked": [],
            "disliked": []
        }
