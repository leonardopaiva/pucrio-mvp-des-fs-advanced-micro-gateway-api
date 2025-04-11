import os
import json
from flask import request, jsonify, redirect
from flask_openapi3 import OpenAPI, Info, Tag
from flask_cors import CORS
import requests
import pudb
import enum
from datetime import datetime

from models import GenericSchema, AuthHeader
from schemas.queue import ProcessSyncSchema
from schemas.event import EventBuscaIdSchema, EventSchema, EventBuscaSchema
from services.token_service import verify_token
from services.auth_service import (
    login_auth,
    reset_password_auth,
    sign_up_auth,
    confirm_sign_up_auth,
    refresh_token_auth
)
from config import MICRO_QUEUE_API_URL, MICRO_APPOINTMENTS_URL
from pydantic import BaseModel, Field

# Default bearer token cache used when no Authorization header is provided.
DEFAULT_BEARER_TOKEN_CACHE = os.getenv("DEFAULT_BEARER_TOKEN", "")

info = Info(
    title="Micro Gateway API",
    version="1.0.0",
    description=(
        "# Important Note\n\n"
        "This is the main component (microservice) of MVP 3. "
        "It receives front-end requests and forwards them to other microservices, acting as a proxy to protect authenticated routes."
    )
)
app = OpenAPI(__name__, info=info)
CORS(app)

# Definition of tags for documentation
auth_tag = Tag(
    name="Micro Authentication API", 
    description="Authentication routes for the micro‑auth‑api (you can log in, copy the token and set it to make the authenticated routes work; authentication is performed using Amazon Cognito, external API)"
)
queue_tag = Tag(
    name="Micro Queue API", 
    description="Endpoints for item synchronization (authentication required)"
)
appointments_tag = Tag(
    name="Micro Appointments API", 
    description="Endpoints for retrieving and manipulating appointments (authentication required)"
)

def json_converter(o):
    if isinstance(o, enum.Enum):
        return o.value
    if isinstance(o, datetime):
        return o.isoformat()
    return str(o)

class SetBearerTokenSchema(BaseModel):
    new_token: str = Field(..., description="New AccessToken that will be used as the default in the gateway")

# get_user_id_from_request
# Extracts and validates the Authorization token from the incoming request,
# then returns the user ID (from the token's 'sub' field) and the full header.
# Steps:
#   1. Attempt to get the "Authorization" header from the request.
#   2. If missing, attempt to use the default bearer token.
#   3. Validate that the header is in the format "Bearer <token>".
#   4. Validate the token using `verify_token()`.
#   5. Extract the "sub" field as user_id. All subsequent requests use this user_id.
def get_user_id_from_request():
    """
    Extracts and validates the Authorization token from the request and returns the user_id (from the 'sub' field)
    along with the complete header. Raises an exception if anything is wrong.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        # Use the default token if not provided
        if not DEFAULT_BEARER_TOKEN_CACHE:
            raise ValueError("Missing Authorization header")
        auth_header = f"Bearer {DEFAULT_BEARER_TOKEN_CACHE}"
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
    return user_id, auth_header

@app.get('/')
def home():
    """Redirects to the OpenAPI documentation."""
    return redirect('/openapi')

@app.get('/hello-world')
def hello_world():
    """Returns a simple hello world."""
    print('testessssssss', flush=True)
    return jsonify({"message": "Hello World"})

# ---- ******************* ----
# MICRO AUTH API
# ---- ******************* ----
@app.post('/auth/login', tags=[auth_tag])
def login(body: GenericSchema):
    """
    Performs user login.

    Expected parameters (body):
      - username: Example: "leonardopaiva.test@gmail.com"
      - password: Example: "enter_your_password"
      
    Returns:
      Access and refresh tokens if successful.
    """
    payload = body.dict(exclude_unset=True)
    headers = {"Content-Type": "application/json"}
    data, status = login_auth(payload, headers)
    return jsonify(data), status

@app.post('/auth/reset-password', tags=[auth_tag])
def reset_password(body: GenericSchema):
    """
    Initiates the user password reset process.
    """
    payload = body.dict(exclude_unset=True)
    headers = {"Content-Type": "application/json"}
    data, status = reset_password_auth(payload, headers)
    return jsonify(data), status

@app.post('/auth/sign-up', tags=[auth_tag])
def sign_up(body: GenericSchema):
    """
    Registers a new user.

    Expected parameters (body):
      - name: The full name of the user.
      - password: The user's password.
      - username: The user's email (should be the same as the email field).
      - email: The user's email.
      
    NOTE: The username field must be filled with the email.
    
    Returns:
      JSON response indicating success or failure.
    """
    payload = body.dict(exclude_unset=True)
    headers = {"Content-Type": "application/json"}
    data, status = sign_up_auth(payload, headers)
    return jsonify(data), status

@app.post('/auth/confirm-sign-up', tags=[auth_tag])
def confirm_sign_up(body: GenericSchema):
    """
    Confirms user registration.

    Expected parameters (body):
      - username: The user's email.
      - confirmation_code: The confirmation code received via email.
      
    Returns:
      A success message if the registration is confirmed.
    """
    payload = body.dict(exclude_unset=True)
    headers = {"Content-Type": "application/json"}
    data, status = confirm_sign_up_auth(payload, headers)
    return jsonify(data), status

@app.post('/auth/refresh-token', tags=[auth_tag])
def refresh_token(body: GenericSchema):
    """
    Updates the access token.

    Expected parameters (body):
      - username: Must be the user's email.
      - refreshToken: Refresh token obtained during login.
      
    Returns:
      A new access token if the operation is successful.
    """
    payload = body.dict(exclude_unset=True)
    headers = {"Content-Type": "application/json"}
    data, status = refresh_token_auth(payload, headers)
    if data.get("status") == "ok":
        return jsonify(data.get("data", {})), status
    else:
        return jsonify(data), status

# Set the bearer token useful for Swagger operations
@app.post('/auth/set-bearer-token', tags=[auth_tag])
def set_auth_bearer_token(body: SetBearerTokenSchema):
    """
    Updates the global default Bearer token.

    IMPORTANT:
      Remove in production
    """
    global DEFAULT_BEARER_TOKEN_CACHE
    DEFAULT_BEARER_TOKEN_CACHE = body.new_token
    return jsonify({
        "status": "ok",
        "msg": "Bearer token updated successfully.",
        "data": {"new_token": body.new_token}
    }), 200

# ---- ******************* ----
# MICRO QUEUE API
# ---- ******************* ----
# Sends the queue data to the queue micro API.
# This is the main route of this MVP, responsible for user data synchronization.
@app.post(
    '/queue/process-sync',
    tags=[queue_tag],
    description=(
        """
        {
          "items": [
            {
              "id": "1",
              "domain": "appointment",
              "action": "create",
              "data": { "key": "value" }
            },
            {
              "id": "2",
              "domain": "doctor",
              "action": "update",
              "data": { "key": "value" }
            }
          ]
        }
        """
    )
)
def process_sync(body: ProcessSyncSchema):
    """
    Forwards the request to the micro-queue-api,
    extracting the user ID from the Authorization token and inserting it into the "data" object of each item in the payload.
    If the header is not provided, the updated default token is used.
    """
    payload = body.dict(exclude_unset=True)
    try:
        user_id, auth_value = get_user_id_from_request()
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 401

    items = payload.get("items", [])
    for idx, item in enumerate(items):
        if isinstance(item, dict):
            if "data" not in item or not isinstance(item["data"], dict):
                item["data"] = {}
            item["data"]["user_id"] = user_id
        else:
            return jsonify({"status": "error", "msg": f"Item at index {idx} is not a valid object", "data": {}}), 400
    payload["items"] = items

    try:
        payload = json.loads(json.dumps(payload, default=json_converter))
    except Exception as e:
        return jsonify({"status": "error", "msg": f"Error serializing payload: {str(e)}", "data": {}}), 500

    headers = {"Content-Type": "application/json", "Authorization": auth_value}
    try:
        response = requests.post(f"{MICRO_QUEUE_API_URL}/process-sync", json=payload, headers=headers)
        response_data = response.json()
        if any("error" in item for item in response_data.get("data", [])):
            return jsonify({
                "status": "error",
                "msg": "Some items failed to process.",
                "data": response_data.get("data", [])
            }), 400
        return jsonify(response_data), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 500

# ---- ******************* ----
# MICRO APPOINTMENTS API
# ---- ******************* ----
@app.get(
    '/appointments',
    tags=[appointments_tag],
    description=(
        """
        Retrieves the user's appointments.
        """
    )
)
def get_appointments():
    """
    Retrieves the list of appointments for the authenticated user.
    """
    try:
        user_id, auth_value = get_user_id_from_request()
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 401

    url = f"{MICRO_APPOINTMENTS_URL.rstrip('/')}/appointments?user_id={user_id}"
    headers = {"Authorization": auth_value}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return jsonify(response.json()), response.status_code
        return jsonify(response.json()), 200
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 500

@app.delete(
    '/appointment',
    tags=[appointments_tag],
    description=(
        """
        Deletes a specific appointment for the user.
        """
    )
)
def delete_appointment(query: EventBuscaIdSchema):
    """
    Deletes a specific appointment for the authenticated user.
    """
    try:
        user_id, auth_value = get_user_id_from_request()
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 401

    appointment_id = query.id
    url = f"{MICRO_APPOINTMENTS_URL.rstrip('/')}/appointment?id={appointment_id}&user_id={user_id}"
    headers = {"Authorization": auth_value}
    try:
        response = requests.delete(url, headers=headers)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 500

@app.post('/appointment', tags=[appointments_tag],
          description="Forwards the create appointment request to the micro‑appointments‑api.")
def create_appointment(body: EventSchema):
    """
    Creates a new appointment.

    This endpoint extracts the user_id from the Authorization token and inserts it into the payload
    sent to the micro‑appointments‑api, ensuring that the appointment belongs to the authenticated user.
    """
    try:
        user_id, auth_value = get_user_id_from_request()
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 401

    payload = body.dict(exclude_unset=True)
    payload["user_id"] = user_id

    payload = json.loads(json.dumps(payload, default=json_converter))
    
    headers = {"Content-Type": "application/json", "Authorization": auth_value}
    try:
        response = requests.post(f"{MICRO_APPOINTMENTS_URL.rstrip('/')}/appointment", json=payload, headers=headers)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 500

@app.put('/appointment', tags=[appointments_tag],
         description="Forwards the update appointment request to the micro‑appointments‑api.")
def update_appointment(query: EventBuscaSchema, body: EventSchema):
    """
    Updates an existing appointment.

    This endpoint extracts the user_id from the Authorization token and updates the query parameter,
    ensuring that only appointments belonging to the authenticated user are updated.
    """
    try:
        user_id, auth_value = get_user_id_from_request()
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 401

    query.user_id = user_id
    payload = body.dict(exclude_unset=True)

    payload = json.loads(json.dumps(payload, default=json_converter))
    
    headers = {"Content-Type": "application/json", "Authorization": auth_value}
    url = f"{MICRO_APPOINTMENTS_URL.rstrip('/')}/appointment?id={query.id}&user_id={user_id}"
    try:
        response = requests.put(url, json=payload, headers=headers)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e), "data": {}}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
