import os
import random
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.globals import set_debug
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from tools import scan_anime_database, read_anime, upsert_anime, delete_anime, wipe_memory

load_dotenv()

# set_debug(True)

llm = ChatGoogleGenerativeAI(
  model="gemini-3.1-flash-lite",
  temperature=0,
  max_retries=3,
  timeout=20
)

tools = [
  scan_anime_database,
  read_anime,
  upsert_anime,
  delete_anime,
  wipe_memory,
  TavilySearch(
    max_results=5,
    topic="general"
  )
]

with open("prompts/anime_system_prompt.md", "r", encoding="utf-8") as f:
  anime_system_prompt = f.read()

agent = create_agent(
  model=llm,
  tools=tools,
  checkpointer=MemorySaver(),
  system_prompt=anime_system_prompt
)

if __name__ == "__main__":
  print("\nAgent initialized! Type \"exit\" to quit.\n")

  thread_id = str(random.random())

  while True:
    user_question = input("Ask about your anime list: ")
    
    if user_question.lower() == "exit":
      break
        
    try:
      response = agent.invoke({
        "messages": [{
          "role": "user",
          "content": user_question
        }]
      },
      config = {
        "configurable": {
          "thread_id": thread_id
        }
      })

      raw_content = response["messages"][-1].content
      if isinstance(raw_content, list):
        final_message = raw_content[0].get("text", "")
      else:
        final_message = raw_content

      print("\n🤖 Agent:", final_message, "\n")
      print("-" * 50)

      # --- Check for memory wipe
      agent_wiped_memory = False
      
      # Check if the AI decided to call its wipe_memory tool during this turn
      for msg in response["messages"]: 
        if getattr(msg, "type", "") == "tool" and getattr(msg, "name", "") == "wipe_memory":
          agent_wiped_memory = True
          break
      
      if agent_wiped_memory:
        print("[System: The agent decided the task is complete and wiped its memory.]")
        thread_id = str(random.random())

    except Exception as e:
      print(f"An error occurred: {e}")