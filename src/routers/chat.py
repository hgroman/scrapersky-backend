from fastapi import APIRouter, HTTPException
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..models import ChatRequest, ChatResponse
from ..config.settings import Settings

router = APIRouter(prefix="/chat", tags=["chat"])

# Load settings
settings = Settings()

# Initialize LangChain components
chat_model = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    api_key=settings.openai_api_key
)

# Create a simple chain
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant."),
    ("user", "{message}")
])
chain = prompt | chat_model | StrOutputParser()

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that processes messages using LangChain and OpenAI.
    
    Args:
        request (ChatRequest): The chat request containing the message
        
    Returns:
        ChatResponse: The AI's response
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        response = await chain.ainvoke({"message": request.message})
        return ChatResponse(
            response=response,
            model_used="gpt-3.5-turbo"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
