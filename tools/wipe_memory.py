from langchain.tools import tool

@tool
def wipe_memory() -> str:
  """Use this tool ONLY when a task is completely finished. It will clear your short-term memory to save tokens."""

  return "Memory wipe signal sent."