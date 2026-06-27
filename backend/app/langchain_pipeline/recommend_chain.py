import json
import re
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from app.langchain_pipeline.llm import get_llm
from app.langchain_pipeline.prompts import RECOMMENDATION_GENERATION_SYSTEM, RECOMMENDATION_GENERATION_HUMAN

def parse_recommendations(text: str) -> list[dict]:
    """Cleans and parses the recommendation JSON list from the LLM."""
    cleaned = text.strip()
    # Strip markdown block formatting
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()
    
    try:
        data = json.loads(cleaned)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        # Fallback to locate list brackets
        start = cleaned.find('[')
        end = cleaned.rfind(']')
        if start != -1 and end != -1:
            try:
                data = json.loads(cleaned[start:end+1])
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass
        # Return empty list on failure
        return []

def run_recommendation_generation(
    preferences: dict,
    liked_movies: list[str],
    disliked_movies: list[str]
) -> list[dict]:
    """
    Runs the recommendation generation chain.
    Returns a list of dicts with keys 'title' and 'justification'.
    """
    # 0.4 temperature encourages structured outputs with slight creative variety
    llm = get_llm(temperature=0.4)
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(RECOMMENDATION_GENERATION_SYSTEM),
        HumanMessagePromptTemplate.from_template(RECOMMENDATION_GENERATION_HUMAN)
    ])
    
    chain = prompt | llm
    
    # Format list inputs into strings
    liked_str = ", ".join(liked_movies) if liked_movies else "None"
    disliked_str = ", ".join(disliked_movies) if disliked_movies else "None"
    
    # Extract keywords
    keywords_list = preferences.get("sentiment_keywords")
    if isinstance(keywords_list, list):
        keywords_str = ", ".join(keywords_list)
    else:
        keywords_str = str(keywords_list) if keywords_list else "None"
        
    response = chain.invoke({
        "mood": preferences.get("mood") or "Any",
        "genre": preferences.get("genre") or "Any",
        "rating_threshold": preferences.get("rating_threshold") or "Any",
        "sentiment_keywords": keywords_str,
        "liked_movies": liked_str,
        "disliked_movies": disliked_str
    })
    
    return parse_recommendations(response.content)
