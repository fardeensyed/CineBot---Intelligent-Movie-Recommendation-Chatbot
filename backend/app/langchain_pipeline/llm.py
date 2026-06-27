import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# We use llama-3.3-70b-versatile as the current recommended versatile model on Groq.
DEFAULT_MODEL = "llama-3.3-70b-versatile"

def get_llm(model_name: str = DEFAULT_MODEL, temperature: float = 0.0) -> ChatGroq:
    """
    Initializes and returns the ChatGroq model.
    Reads GROQ_API_KEY from environment variables.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        # Prompt developer / user to configure it
        raise ValueError(
            "GROQ_API_KEY environment variable not found. "
            "Please create a .env file under /backend with your GROQ_API_KEY."
        )
        
    return ChatGroq(
        model_name=model_name,
        temperature=temperature,
        api_key=api_key
    )
