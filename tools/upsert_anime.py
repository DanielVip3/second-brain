from typing import Optional
import requests
from langchain.tools import tool
from tools.common import API_HEADERS, NOCODB_ANIME_API_URL

@tool
def upsert_anime(
  Title: str,
  Status: str,
  Seasons: Optional[int] = None,
  Episodes: Optional[int] = None,
  Year: Optional[int] = None,
  Continuation: Optional[str] = None,
  Coverage: Optional[str] = None,
  Source: Optional[str] = None
) -> str:
  """Use this tool to update or insert an anime into the database."""
  
  response = requests.post(
    NOCODB_ANIME_API_URL+"/upsert",
    headers=API_HEADERS,
    json={
      "fieldsToMergeOn": ["Title"],
      "records": {
        "fields": {
          "Title": Title,
          "Status": Status,
          "Seasons": Seasons,
          "Episodes": Episodes,
          "Year": Year,
          "Continuation": Continuation,
          "Coverage": Coverage,
          "Source": Source
        }
      }
    }
  )
  
  if response.status_code == 200:
    return f"Successfully upserted {Title} to NocoDB!"
  else:
    return f"Failed to upsert anime. API Error: {response.text}"