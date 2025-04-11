import requests
from jose import jwt, JWTError
from config import COGNITO_APP_CLIENT_ID, COGNITO_ISSUER, AWS_REGION, COGNITO_USER_POOL_ID

def get_cognito_jwk():
    """
    Retrieve the Cognito public keys for validating JWT tokens.
    """
    jwks_url = f"{COGNITO_ISSUER}/.well-known/jwks.json"
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()

def verify_token(token: str) -> dict:
    """
    Verify and decode the JWT token using the Cognito public keys.
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
