import os
import getpass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")
_set_env("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "langchain-academy"

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)


def call_ai(prompt: str, **kwargs) -> str:
    """
    Abstraction for all AI calls. Accepts a prompt parameter and returns the AI response.
    
    Args:
        prompt: The prompt string to send to the AI
        **kwargs: Additional variables to pass to the prompt template
        
    Returns:
        The AI response as a string
    """
    prompt_template = ChatPromptTemplate.from_template(prompt)
    chain = prompt_template | llm
    response = chain.invoke(kwargs)
    return response.content
