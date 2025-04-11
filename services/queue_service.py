import json
import requests
from config import MICRO_QUEUE_API_URL
from services.token_service import verify_token

def get_user_id_from_token(auth_header: str) -> str:
    """
    Verifies and extracts the user_id from the authorization token.
    """
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ValueError("Invalid Authorization header format")

    token = parts[1]
    token_payload = verify_token(token)
    if not token_payload:
        raise ValueError("Invalid or expired token")

    user_id = token_payload.get("sub")
    if not user_id:
        raise ValueError("User ID not found in token")

    return user_id

def prepare_payload_with_user_id(payload: dict, user_id: str) -> dict:
    """
    For each item in the payload, add the user_id inside the 'data' object.
    """
    items = payload.get("items", [])
    for idx, item in enumerate(items):
        if isinstance(item, dict):
            if "data" not in item or not isinstance(item["data"], dict):
                item["data"] = {}
            item["data"]["user_id"] = user_id
        else:
            raise ValueError(f"Item at index {idx} is not a valid object")

    payload["items"] = items
    return payload

def send_sync_request(payload: dict, headers: dict) -> dict:
    """
    Sends the request to the micro‑queue‑api.
    """
    try:
        response = requests.post(f"{MICRO_QUEUE_API_URL}/process-sync", json=payload, headers=headers)
        response_data = response.json()
        return response_data
    except Exception as e:
        raise Exception(f"Error in sending sync request: {str(e)}")

def process_sync_payload(payload: dict, auth_header: str) -> dict:
    """
    Processes the synchronization payload.
    """
    user_id = get_user_id_from_token(auth_header)
    payload = prepare_payload_with_user_id(payload, user_id)

    try:
        payload = json.loads(json.dumps(payload, default=str))
    except Exception as e:
        raise Exception(f"Error serializing payload: {str(e)}")

    response_data = send_sync_request(payload, headers={"Content-Type": "application/json", "Authorization": auth_header})
    return response_data
