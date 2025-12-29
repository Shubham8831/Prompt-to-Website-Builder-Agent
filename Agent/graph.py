from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
load_dotenv()

key = os.getenv("GROQ_API_KEY")

from prompts import *
from states import *

LLM = ChatGroq(model="openai/gpt-oss-120b", api_key=key)

user_prompt="create a simple calculator web application"
prompt = planner_prompt(user_prompt)

response = LLM.with_structured_output(Plan).invoke(prompt)
print(response)