import requests
from langchain.tools import tool
from tools.common import API_HEADERS, NOCODB_ANIME_API_URL

@tool
def scan_anime_database() -> str:
  """Use this tool to read the current list of titles of anime from the database."""

  response = requests.get(
    NOCODB_ANIME_API_URL,
    headers=API_HEADERS,
    params={
      "fields": "Title",
      "pageSize": 10000
    }
  )
  
  titles = []
  if response.status_code == 200:
    records = response.json()["records"]

    for record in records:
      titles.append(record["fields"]["Title"])

    return str(titles)
  else:
    return f"Failed to retrieve data. API Error: {response.text}"