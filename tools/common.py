import os
from dotenv import load_dotenv

load_dotenv()

NOCODB_ANIME_API_URL = os.environ.get("NOCODB_ANIME_API_URL")
NOCODB_AI_AGENT_TOKEN = os.environ.get("NOCODB_AI_AGENT_TOKEN")

API_HEADERS = {
  "xc-token": NOCODB_AI_AGENT_TOKEN,
  "Content-Type": "application/json"
}