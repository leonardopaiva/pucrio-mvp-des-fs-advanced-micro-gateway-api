import requests
from config import MICRO_AUTH_API_URL

def refresh_user_token(username: str, refresh_token: str) -> dict:
    url = f"{MICRO_AUTH_API_URL}/refresh"
    payload = {"username": username, "refreshToken": refresh_token}
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
