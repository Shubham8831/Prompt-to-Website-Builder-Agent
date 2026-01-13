# from langgraph.graph import StateGraph, START, END
# from langchain_groq import ChatGroq
# from langgraph.prebuilt import create_react_agent
# """ReAct = Reason + Act

# The model:

# Thinks (reasoning step)

# Acts (calls a tool)

# Observes the tool output

# Repeats until it can give a final answer

# Typical ReAct loop:

# Thought → Action → Observation → Thought → Action → Observation → Final Answer"""
# import langchain
# langchain.verbose = True # Show human-readable logs of what LangChain is doing internally
# langchain.debug = True # Show low-level, technical logs including full internal stack details
# from tools import write_file, read_file, get_current_directory, list_files

# from typing import TypedDict
# from dotenv import load_dotenv
# import os
# load_dotenv()

# key = os.getenv("GROQ_API_KEY")

# from prompts import *
# from states import *

# LLM = ChatGroq(model="llama-3.3-70b-versatile", api_key=key)

# class MainState(TypedDict):
#     user_prompt :str
#     plan : str
#     task_plan : str
#     code : str
#     coder_state: Optional[CoderState]



# def planner_node(state:MainState) -> MainState:
#     user_prompt = state["user_prompt"]


#     # user_prompt="create a simple calculator web application"
#     prompt = planner_prompt(user_prompt)

#     response = LLM.with_structured_output(Plan).invoke(prompt)

#     state["plan"] = response
#     return state



# def architect_node(state:MainState) -> MainState:
#     plan = state["plan"]
#     prompt = architect_prompt(plan)
#     task_plan = LLM.with_structured_output(TaskPlan).invoke(prompt)

#     if task_plan is None:
#         raise ValueError("Architecture did not return a valid response")

#     state["task_plan"] = task_plan

#     return state



# def coder_node(state: MainState) -> MainState:
#     """LangGraph tool-using coder agent."""
#     coder_state: CoderState = state.get("coder_state")
#     if coder_state is None:
#         coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

#     steps = coder_state.task_plan.implementation_steps
#     if coder_state.current_step_idx >= len(steps):
#         return {"coder_state": coder_state, "status": "DONE"}

#     current_task = steps[coder_state.current_step_idx]
#     existing_content = read_file.invoke(current_task.filepath)

#     system_prompt = coder_system_prompt()
#     user_prompt = (
#         f"Task: {current_task.task_description}\n"
#         f"File: {current_task.filepath}\n"
#         f"Existing content:\n{existing_content}\n" #content already present in the same file
#         "Use write_file(path, content) to save your changes."
#     )

#     coder_tools = [read_file, write_file, list_files, get_current_directory]
#     react_agent = create_react_agent(LLM, coder_tools)

#     react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
#                                      {"role": "user", "content": user_prompt}]})

#     coder_state.current_step_idx += 1
#     state["coder_state"] = coder_state
#     return state

#     # user_prompt = (
#     #     f"Task: {current_task.task_description}\n"
#     # )
#     # system_prompt = coder_system_prompt()

#     # response = LLM.invoke(system_prompt + user_prompt)
#     # state["code"] = response

#     # coder_tools = [read_file, write_file, list_files, get_current_directory]
#     # react_agent = create_agent(LLM, coder_tools)
#     # react_agent.invoke({"messages": [{"role":"system","content" : system_prompt},
#     #                                  {"role":"user", "content":user_prompt}]})
    

#     # return state

# graph = StateGraph(MainState)

# graph.add_node("planner", planner_node)
# graph.add_node("architect", architect_node)
# graph.add_node("coder", coder_node)

# graph.add_edge(START,"planner")
# graph.add_edge("planner", "architect")
# graph.add_edge("architect", "coder")
# graph.add_conditional_edges(
#     "coder",
#     lambda s: "END" if s.get("status") == "DONE" else "coder",
#     {"END": END, "coder": "coder"}
# )

# graph.set_entry_point("planner")
# workflow = graph.compile()


# output_state = workflow.invoke({"user_prompt": "make a simple web based calculator"})
# print(output_state)



from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from typing import TypedDict, Literal
from dotenv import load_dotenv
import os

import langchain
langchain.verbose = True
langchain.debug = True

from tools import write_file, read_file, get_current_directory, list_files
from prompts import *
from states import *

load_dotenv()
key = os.getenv("GROQ_API_KEY")

LLM = ChatGroq(model="llama-3.3-70b-versatile", api_key=key)

class MainState(TypedDict):
    user_prompt: str
    plan: Plan
    task_plan: TaskPlan
    code: str
    coder_state: Optional[CoderState]


def planner_node(state: MainState) -> MainState:
    user_prompt = state["user_prompt"]
    prompt = planner_prompt(user_prompt)
    response = LLM.with_structured_output(Plan).invoke(prompt)
    state["plan"] = response
    return state


def architect_node(state: MainState) -> MainState:
    plan = state["plan"]
    prompt = architect_prompt(plan)
    task_plan = LLM.with_structured_output(TaskPlan).invoke(prompt)

    if task_plan is None:
        raise ValueError("Architecture did not return a valid response")

    state["task_plan"] = task_plan
    return state


def coder_node(state: MainState) -> MainState:
    """LangGraph tool-using coder agent."""
    coder_state = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

    steps = coder_state.task_plan.implementation_steps
    
    # If all tasks are done, just return the state
    if coder_state.current_step_idx >= len(steps):
        state["coder_state"] = coder_state
        return state

    current_task = steps[coder_state.current_step_idx]
    
    # Read existing content safely
    try:
        existing_content = read_file.invoke({"path": current_task.filepath})
    except:
        existing_content = ""

    system_prompt = coder_system_prompt()
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )

    coder_tools = [read_file, write_file, list_files, get_current_directory]
    react_agent = create_react_agent(LLM, coder_tools)

    print(f"\n{'='*60}")
    print(f"Processing Task {coder_state.current_step_idx + 1}/{len(steps)}")
    print(f"File: {current_task.filepath}")
    print(f"{'='*60}\n")

    react_agent.invoke({
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    })

    coder_state.current_step_idx += 1
    state["coder_state"] = coder_state
    return state


def should_continue_coding(state: MainState) -> Literal["coder", "end"]:
    """Check if there are more tasks to process."""
    coder_state = state.get("coder_state")
    
    # If no coder_state exists yet, continue to coder
    if coder_state is None:
        return "coder"
    
    steps = coder_state.task_plan.implementation_steps
    
    # If current index is less than total steps, continue coding
    if coder_state.current_step_idx < len(steps):
        print(f"\nContinuing: {coder_state.current_step_idx}/{len(steps)} tasks completed\n")
        return "coder"
    else:
        print(f"\nAll {len(steps)} tasks completed!\n")
        return "end"


# Build the graph
graph = StateGraph(MainState)

graph.add_node("planner", planner_node)
graph.add_node("architect", architect_node)
graph.add_node("coder", coder_node)

# Add edges
graph.add_edge(START, "planner")
graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")

# Add conditional edge for looping
graph.add_conditional_edges(
    "coder",
    should_continue_coding,
    {
        "coder": "coder",  # Loop back to process next task
        "end": END         # All done, exit
    }
)

workflow = graph.compile()

# Run the workflow
print("\n" + "="*60)
print("STARTING WORKFLOW")
print("="*60 + "\n")

output_state = workflow.invoke({"user_prompt": "make a simple web based calculator"})

print("\n" + "="*60)
print("WORKFLOW COMPLETE")
print("="*60)
print(f"Total tasks: {len(output_state['task_plan'].implementation_steps)}")
print(f"Tasks completed: {output_state['coder_state'].current_step_idx}")
print("="*60 + "\n")