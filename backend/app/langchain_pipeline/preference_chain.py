import json
import re
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from app.langchain_pipeline.llm import get_llm
from app.langchain_pipeline.prompts import PREFERENCE_EXTRACTION_SYSTEM, PREFERENCE_EXTRACTION_HUMAN

def parse_json_response(text: str) -> dict:
    """Helper to clean and parse JSON response from LLM."""
    cleaned = text.strip()
    # Strip markdown block formatting if the LLM added it
    cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to locate JSON boundaries as a fallback
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start:end+1])
            except json.JSONDecodeError:
                pass
        # Final fallback
        return {
            "mood": None,
            "genre": None,
            "rating_threshold": None,
            "sentiment_keywords": []
        }

def run_preference_extraction(message: str, history: str) -> dict:
    """
    Executes the preference extraction chain.
    Accepts the user message and conversation history, returning a dict of extracted preferences.
    """
    llm = get_llm(temperature=0.0)  # Temperature 0.0 for deterministic extraction
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(PREFERENCE_EXTRACTION_SYSTEM),
        HumanMessagePromptTemplate.from_template(PREFERENCE_EXTRACTION_HUMAN)
    ])
    
    chain = prompt | llm
    
    response = chain.invoke({
        "message": message,
        "history": history
    })
    
    return parse_json_response(response.content)
