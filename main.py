from langchain_groq import ChatGroq
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("GROQ_API_KEY")

class ext(BaseModel):
    name: str
    marks: int

model = ChatGroq(
    model="openai/gpt-oss-120b", api_key=key                 
)

llm = model.with_structured_output(ext)

ans = llm.invoke("hello my name is shubham and i got 10 marks")
print(ans)
