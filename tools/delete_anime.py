import requests
from langchain.tools import tool
from tools.common import API_HEADERS, NOCODB_ANIME_API_URL

@tool
def delete_anime(id: int) -> int:
  """Use this tool to remove an anime from the database."""
  
  response = requests.delete(
    NOCODB_ANIME_API_URL,
    headers=API_HEADERS,
    json={
      "Id": id,
    }
  )
  
  if response.status_code == 200:
    return f"Successfully removed {id} from NocoDB!"
  else:
    return f"Failed to add anime. API Error: {response.text}"