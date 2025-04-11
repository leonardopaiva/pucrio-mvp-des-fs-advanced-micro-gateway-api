# micro-gateway-app/decorators.py
import os
from flask import request, jsonify
from services.token_service import verify_token

DEFAULT_BEARER_TOKEN = os.getenv("DEFAULT_BEARER_TOKEN", None)

def token_required(func):
    def wrapper(*args, **kwargs):
        print("*****1111***")
        auth_header = request.headers.get("Authorization")
        # Se não houver header, tenta usar o token padrão (útil para testes via Swagger)
        print("****2222****")
        if not auth_header and DEFAULT_BEARER_TOKEN:
            auth_header = f"Bearer {DEFAULT_BEARER_TOKEN}"
            print("*****3333***")
            print(auth_header)
        if not auth_header:
            return jsonify({"status": "error", "msg": "Missing Authorization header", "data": {}}), 401
        parts = auth_header.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            return jsonify({"status": "error", "msg": "Invalid Authorization header format", "data": {}}), 401
        token = parts[1]
        print("Token recebido para validação:", token)
        payload = verify_token(token)
        if not payload:
            return jsonify({"status": "error", "msg": "Invalid or expired token", "data": {}}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
