import requests
from langchain.tools import tool
from tools.common import API_HEADERS, NOCODB_ANIME_API_URL

@tool
def read_anime(title: str) -> str:
  """Use this tool to read an anime from the database by its title."""

  response = requests.get(
    NOCODB_ANIME_API_URL,
    headers=API_HEADERS,
    params={
      "where": f"(Title,eq,{title})"
    }
  )
  
  if response.status_code == 200:
    data = response.json()
    print(data)

    return str(data)
  else:
    return f"Failed to retrieve data. API Error: {response.text}"