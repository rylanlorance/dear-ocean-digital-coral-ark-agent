from fileinput import filename
import os
import getpass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from IPython.display import Image, display
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import Field, BaseModel
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

llm = ChatOpenAI(model="gpt-4o", temperature=0)


class DCA_Agent_State(BaseModel):
    filename: str = Field(
        description="The filename of the coral species data to be processed."
    ),
    filename_valid: bool = Field(
        default=False,
        description="Indicates whether the provided filename has been validated successfully."
    )


def central_executor(state: DCA_Agent_State) -> DCA_Agent_State:
    # Create routing prompt

    routing_prompt = ChatPromptTemplate.from_messages([
        ("system", """
      You are the central executor for a Digital Coral Ark Agent.
      Your role is to analyze the current state and determine the next best action.
  
      If the filename provided is valid and accessible, proceed to the final data return step. 
      
      Current filename: {filename}
      Current filename valid: {filename_valid}
      Available actions:
        - "validate_filepath": Validate the provided filename based on a given schema.
        - "return_final_data": Return the final processed data.       
      """
      )])
    messages = routing_prompt.format_messages(
        filename=state.filename,
        filename_valid=state.filename_valid
    )

    response = llm.invoke(messages)
    return state
  
def filepath_validate(state: DCA_Agent_State) -> DCA_Agent_State:
    if state.filename.endswith('.JPG'):
        state.filename_valid = True
    else:
        state.filename_valid = False
    return state
  
def return_final_data(state: DCA_Agent_State) -> DCA_Agent_State:
    if state.filename_valid:
        print(f"Final data returned for file: {state.filename}")
    else:
        print("Filename is not valid. Cannot return final data.")
    return state

builder = StateGraph(DCA_Agent_State)

builder.add_node("executor", central_executor)

builder.add_edge(START, "executor")
builder.add_node("filepath_validator", filepath_validate)
builder.add_node("return_final_data", return_final_data)
builder.add_conditional_edges(
  "executor",
  {
    "validate_filepath": filepath_validate,
    "return_final_data": return_final_data
  }
)

# Add the return path from validator to executor:
builder.add_edge("filepath_validator", "executor")

# End workflow only after returning final data:
builder.add_edge("return_final_data", END)


memory = MemorySaver()
graph = builder.compile(checkpointer=memory)


def run_agent_workflow(filename: str):
  initial_state = DCA_Agent_State(filename=filename)
  
  config = {"configurable": {"thread_id": f"coral_workflow_{filename}"}}

  for step in graph.stream(initial_state, config):
      for node_name, node_state in step.items():
          print(f"Node: {node_name}, State: {node_state}")
  


if __name__ == "__main__":
    # Example usage
    run_agent_workflow("/Users/rylanlorance/Dear_Ocean/Dear_Ocean_Digital_Coral_Ark_Agent/data/input/Antler Coral Pocillopora eydouxi entangled Hanauma Bay 20210421_25_Roberts_Anke - HAN.JPG")