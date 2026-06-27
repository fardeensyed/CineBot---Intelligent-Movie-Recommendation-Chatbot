try:
    from langchain_classic.memory import ConversationBufferMemory
except ImportError:
    try:
        from langchain.memory import ConversationBufferMemory
    except ImportError:
        # Fallback to langchain_community if needed
        from langchain_community.memory import ConversationBufferMemory

# In-memory store for session memories.
# NOTE: For a production application, this should be moved to a distributed, persistent store
# like Redis (e.g., using LangChain's RedisChatMessageHistory) to prevent memory leaks and
# support scaling across multiple backend instances.
_session_memories = {}

def get_memory(session_id: str) -> ConversationBufferMemory:
    """
    Retrieves or creates a ConversationBufferMemory instance for the given session_id.
    Uses 'history' as the memory key to match our prompt templates.
    """
    if session_id not in _session_memories:
        _session_memories[session_id] = ConversationBufferMemory(
            memory_key="history",
            return_messages=True
        )
    return _session_memories[session_id]

def clear_memory(session_id: str) -> None:
    """Clears conversation memory for a session."""
    if session_id in _session_memories:
        _session_memories[session_id].clear()
