import os
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

async def ask_agent(user_prompt: str, thread_id: str):
  agent_wiped_memory = False

  try:
    events = agent.astream_events({
      "messages": [{
        "role": "user",
        "content": user_prompt
      }]
    },
    config = {
      "configurable": {
        "thread_id": thread_id
      }
    },
    version="v2")

    async for event in events:
      kind = event["event"]

      if kind == "on_chat_model_stream":
        chunk = event["data"]["chunk"]
        text = ""

        if chunk.content and isinstance(chunk.content, str):
          text = chunk.content
        elif chunk.content and isinstance(chunk.content, list):
          for block in chunk.content:
            if isinstance(block, dict) and "text" in block and block["text"]:
              text = block["text"]
            elif isinstance(block, str) and block:
              text = block
        
        if text:
          yield {"type": "token", "content": text}
        
      elif kind == "on_tool_start":
        tool_name = event["name"]

        # --- Check for memory wipe
        if tool_name == "wipe_memory":
          agent_wiped_memory = True
        
        yield {"type": "tool_status", "content": f"\n\n⚙️ [Running tool: {tool_name}...]\n\n"}

    if agent_wiped_memory:
      yield {"type": "memory_wiped", "content": True}

  except Exception as e:
    yield {"type": "error", "content": str(e)}