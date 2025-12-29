from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
import langchain
langchain.verbose = True # Show human-readable logs of what LangChain is doing internally
langchain.debug = True # Show low-level, technical logs including full internal stack details

from typing import TypedDict
from dotenv import load_dotenv
import os
load_dotenv()

key = os.getenv("GROQ_API_KEY")

from prompts import *
from states import *

LLM = ChatGroq(model="openai/gpt-oss-120b", api_key=key)

class MainState(TypedDict):
    user_prompt :str
    plan : str
    task_plan : str
    code : str



def planner_node(state:MainState) -> MainState:
    user_prompt = state["user_prompt"]


    # user_prompt="create a simple calculator web application"
    prompt = planner_prompt(user_prompt)

    response = LLM.with_structured_output(Plan).invoke(prompt)

    state["plan"] = response
    return state



def architect_node(state:MainState) -> MainState:
    plan = state["plan"]
    prompt = architect_prompt(plan)
    task_plan = LLM.with_structured_output(TaskPlan).invoke(prompt)

    if task_plan is None:
        raise ValueError("Architecture did not return a valid response")

    state["task_plan"] = task_plan

    return state



def coder_node(state:MainState)-> MainState:
    steps = state["task_plan"].implementation_steps # task plan has list of implemetation steps [file path and desctipiton]
    current_step_idx = 0
    current_task = steps[current_step_idx]

    user_prompt = (
        f"Task: {current_task.task_description}\n"
    )
    system_prompt = coder_system_prompt()

    response = LLM.invoke(system_prompt + user_prompt)
    state["code"] = response

    return state

graph = StateGraph(MainState)

graph.add_node("planner", planner_node)
graph.add_node("architect", architect_node)
graph.add_node("coder", coder_node)

graph.add_edge(START,"planner")
graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_edge("coder", END)

workflow = graph.compile()


output_state = workflow.invoke({"user_prompt": "make a simple web based calculator"})
print(output_state)