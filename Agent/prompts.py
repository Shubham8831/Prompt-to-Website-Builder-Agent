
# takes user request and returns complete project plan
def planner_prompt(user_prompt: str) -> str:
    PLANNER_PROMPT = f"""
you are the PLANNER agent. complete engineering project plan.

user request : 
{user_prompt}
"""
    return PLANNER_PROMPT