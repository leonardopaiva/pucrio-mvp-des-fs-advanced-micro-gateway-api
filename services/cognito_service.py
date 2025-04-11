import os
import hmac
import hashlib
import base64
import boto3
from botocore.exceptions import ClientError
from jose import jwt, JWTError
import requests

# ENV variables
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.environ.get("COGNITO_APP_CLIENT_ID")
COGNITO_APP_CLIENT_SECRET = os.environ.get("COGNITO_APP_CLIENT_SECRET")  # NOVA VARIÁVEL
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"

# Cognito Client
client = boto3.client('cognito-idp', region_name=AWS_REGION)

def get_secret_hash(username: str) -> str:
    message = username + COGNITO_APP_CLIENT_ID
    dig = hmac.new(
        COGNITO_APP_CLIENT_SECRET.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()

def authenticate_user(username: str, password: str) -> dict:
    try:
        auth_parameters = {
            'USERNAME': username,
            'PASSWORD': password,
            'SECRET_HASH': get_secret_hash(username)
        }
        response = client.initiate_auth(
            ClientId=COGNITO_APP_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters=auth_parameters
        )
        return response.get("AuthenticationResult", response)
    except ClientError as e:
        return {"error": e.response["Error"]["Message"]}

def reset_user_password(username: str) -> dict:
    try:
        response = client.admin_reset_user_password(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username
        )
        return {"message": "Password reset requested successfully."}
    except ClientError as e:
        return {"error": e.response["Error"]["Message"]}

def sign_up_user(username: str, password: str, email: str, name: str) -> dict:
    try:
        response = client.sign_up(
            ClientId=COGNITO_APP_CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'name', 'Value': name}
            ],
            SecretHash=get_secret_hash(username)
        )
        return response
    except ClientError as e:
        return {"error": e.response["Error"]["Message"]}

def confirm_sign_up(username: str, confirmation_code: str, session: str = None) -> dict:
    try:
        params = {
            'ClientId': COGNITO_APP_CLIENT_ID,
            'Username': username,
            'ConfirmationCode': confirmation_code,
            'SecretHash': get_secret_hash(username)
        }
        if session:
            params['Session'] = session

        response = client.confirm_sign_up(**params)
        return {"message": "User confirmed successfully."}
    except ClientError as e:
        return {"error": e.response["Error"]["Message"]}

def get_cognito_jwk():
    """
    Retrieves the Cognito public keys for validating JWT tokens.
    """
    jwks_url = f"{COGNITO_ISSUER}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()

def verify_token(token: str) -> dict:
    """
    Verifies and decodes the JWT token using the Cognito public keys.
    """
    try:
        jwks = get_cognito_jwk()
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")
        key = None
        for jwk in jwks["keys"]:
            if jwk["kid"] == kid:
                key = jwk
                break
        if key is None:
            return None
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=COGNITO_APP_CLIENT_ID,
            issuer=COGNITO_ISSUER
        )
        return payload
    except JWTError:
        return None
    except Exception:
        return None
