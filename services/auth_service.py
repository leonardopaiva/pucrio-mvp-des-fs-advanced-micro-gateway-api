import requests
from config import MICRO_AUTH_API_URL

def login_auth(payload, headers):
    try:
        response = requests.post(f"{MICRO_AUTH_API_URL}/login", json=payload, headers=headers)
        return response.json(), response.status_code
    except Exception as e:
        return {"status": "error", "msg": str(e), "data": {}}, 500

def reset_password_auth(payload, headers):
    try:
        response = requests.post(f"{MICRO_AUTH_API_URL}/reset-password", json=payload, headers=headers)
        return response.json(), response.status_code
    except Exception as e:
        return {"status": "error", "msg": str(e), "data": {}}, 500

def sign_up_auth(payload, headers):
    try:
        response = requests.post(f"{MICRO_AUTH_API_URL}/sign-up", json=payload, headers=headers)
        return response.json(), response.status_code
    except Exception as e:
        return {"status": "error", "msg": str(e), "data": {}}, 500

def confirm_sign_up_auth(payload, headers):
    try:
        response = requests.post(f"{MICRO_AUTH_API_URL}/confirm-sign-up", json=payload, headers=headers)
        return response.json(), response.status_code
    except Exception as e:
        return {"status": "error", "msg": str(e), "data": {}}, 500

def refresh_token_auth(payload, headers):
    try:
        response = requests.post(f"{MICRO_AUTH_API_URL}/refresh-token", json=payload, headers=headers)
        return response.json(), response.status_code
    except Exception as e:
        return {"status": "error", "msg": str(e), "data": {}}, 500
