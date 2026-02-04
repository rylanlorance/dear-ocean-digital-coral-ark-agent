import os
import getpass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from IPython.display import Image, display
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from models import DCA_Agent_State, CommonNameCandidate
from common_name_extractor import extract_common_name_candidates

# Load environment variables from .env file
load_dotenv()

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


_set_env("OPENAI_API_KEY")

_set_env("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_PROJECT"] = "langchain-academy"

llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Create the agentic workflow
builder = StateGraph(DCA_Agent_State)

# Add the extract_common_name_candidates node
builder.add_node("extract_common_name_candidates", extract_common_name_candidates)

# Set up the workflow edges
builder.add_edge(START, "extract_common_name_candidates")
builder.add_edge("extract_common_name_candidates", END)

# Compile the graph
graph = builder.compile()

# Example usage function
def run_workflow(input_filename: str):
    """
    Run the workflow with a given input filename.
    
    Args:
        input_filename: The filename to process
        
    Returns:
        The final state after processing
    """
    initial_state = DCA_Agent_State(
        input_filename=input_filename,
        output_filename="",
        common_name_candidates=[]
    )
    
    result = graph.invoke(initial_state)
    return result

# Example usage
if __name__ == "__main__":
    input_filename = "../data/input/Antler Coral Pocillopora eydouxi entangled Hanauma Bay 20210421_25_Roberts_Anke - HAN.JPG"
    result = run_workflow(input_filename)
    print(result)


