from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from app.langchain_pipeline.llm import get_llm
from app.langchain_pipeline.prompts import RESPONSE_PHRASING_SYSTEM, RESPONSE_PHRASING_HUMAN

def run_response_phrasing(user_message: str, matched_movies: list[dict]) -> str:
    """
    Runs the response phrasing chain.
    Generates a conversational introduction wrapper around the matching movies.
    """
    # 0.7 temperature is good for natural, conversational dialogue phrasing
    llm = get_llm(temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(RESPONSE_PHRASING_SYSTEM),
        HumanMessagePromptTemplate.from_template(RESPONSE_PHRASING_HUMAN)
    ])
    
    # Format the matched catalog details for context
    movies_info_parts = []
    for idx, movie in enumerate(matched_movies, 1):
        movies_info_parts.append(
            f"{idx}. {movie['title']} ({movie['year']}) - "
            f"Genre: {movie['genre']}, Rating: {movie['rating']}\n"
            f"Overview: {movie['overview']}"
        )
        
    movies_info = "\n\n".join(movies_info_parts) if movies_info_parts else "No movies matched from the catalog."
    
    chain = prompt | llm
    
    response = chain.invoke({
        "matched_movies_info": movies_info,
        "user_message": user_message
    })
    
    return response.content.strip()
