import os

# Configurações do Flask
FLASK_APP = os.environ.get("FLASK_APP", "app.py")
FLASK_ENV = os.environ.get("FLASK_ENV", "development")
SECRET_KEY = os.environ.get("COGNITO_APP_CLIENT_SECRET")  # Usando o client secret como SECRET_KEY

# URLs dos microsserviços
MICRO_APPOINTMENTS_URL = os.environ.get("MICRO_APPOINTMENTS_URL")
MICRO_DOCTORS_URL = os.environ.get("MICRO_DOCTORS_URL")
MICRO_ADDRESS_URL = os.environ.get("MICRO_ADDRESS_URL")
MICRO_QUEUE_API_URL = os.environ.get("MICRO_QUEUE_API_URL")
MICRO_AUTH_API_URL = os.environ.get("MICRO_AUTH_API_URL")

# Configurações do Cognito
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.environ.get("COGNITO_APP_CLIENT_ID")
AWS_REGION = os.environ.get("AWS_REGION")

# Monta a URL do Cognito Issuer com base no AWS_REGION e no COGNITO_USER_POOL_ID
COGNITO_ISSUER = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"

# Outras configurações
DEFAULT_BEARER_TOKEN = os.environ.get("DEFAULT_BEARER_TOKEN")
