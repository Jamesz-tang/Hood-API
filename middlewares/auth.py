import base64
import hashlib
import hmac
import json
import os
import time

import boto3
import requests
from botocore.exceptions import ClientError
from flask import request, jsonify
from jose import jwt

# AWS Cognito details (replace with your actual values)
USER_POOL_ID = os.environ.get('USER_POOL_ID')
APP_CLIENT_ID = os.environ.get('APP_CLIENT_ID')
APP_CLIENT_SECRET = os.environ.get('APP_CLIENT_SECRET')  # Client secret if applicable
REGION = os.environ.get('REGION', 'us-east-1')
USERNAME = os.environ.get('USERNAME')


def get_secret_name():
    """
    Get secret name from environment variables.
    :return:
    """
    env = os.getenv('APP_ENV', 'development')
    return f'/smart-packing/{env}/credentials'


def store_or_update_secret(secret_name, secret_value):
    """
    Store or update the secret with the given value.
    :param secret_name:
    :param secret_value:
    :return:
    """
    client = boto3.client('secretsmanager')
    secret_value_json = json.dumps(secret_value)

    try:
        # Attempt to store the secret
        response = client.create_secret(
            Name=secret_name,
            SecretString=secret_value_json
        )
        # print("Secret stored:", response)
    except client.exceptions.ResourceExistsException:
        # If the secret already exists, update it
        response = client.put_secret_value(
            SecretId=secret_name,
            SecretString=secret_value_json
        )
        # print("Secret updated:", response)


# # Example usage
# secret_name = 'my_app/my_secret'
# secret_value = {
#     'access_token': 'your_access_token_value',
#     'refresh_token': 'your_refresh_token_value',
#     'id_token': 'your_id_token_value'
# }
# store_or_update_secret(secret_name, secret_value)


# Function to update environment variable
def update_env_var(variable_name, value):
    os.environ[variable_name] = value


# # Example usage
# update_env_var('MY_SECRET_KEY', 'new_secret_value')

def retrieve_secret(secret_name):
    """
    Retrieve secret value from secret manager.
    :param secret_name:
    :return:
    """
    client = boto3.client('secretsmanager')

    response = client.get_secret_value(
        SecretId=secret_name
    )

    # Retrieve and parse the JSON string
    secret_value_json = response['SecretString']
    secret_value = json.loads(secret_value_json)

    return secret_value


# # Example usage
# secret_name = 'my_app/my_secret'
# secret_value = retrieve_secret(secret_name)
# print("Retrieved Secret:", secret_value)


def get_local_tokens():
    access_token = os.getenv('ACCESS_TOKEN')
    refresh_token_value = os.getenv('REFRESH_TOKEN')
    id_token = os.getenv('ID_TOKEN')
    return {
        'access_token': access_token,
        'refresh_token': refresh_token_value,
        'id_token': id_token
    }


def get_tokens():
    env = os.getenv('ENVIRONMENT', 'development')

    if env == 'production' or env == 'staging':
        # Retrieve tokens from AWS Secrets Manager
        client = boto3.client('secretsmanager')
        secret_name = 'my_app/cognito_tokens'

        response = client.get_secret_value(SecretId=secret_name)
        secret_value_json = response['SecretString']
        secret_value = json.loads(secret_value_json)

    else:
        # Retrieve tokens from environment variables
        secret_value = {
            'access_token': os.getenv('ACCESS_TOKEN'),
            'refresh_token': os.getenv('REFRESH_TOKEN'),
            'id_token': os.getenv('ID_TOKEN')
        }

    return secret_value


def store_tokens(secret_value):
    env = os.getenv('ENVIRONMENT', 'development')

    if env == 'production' or env == 'staging':
        secret_name = 'my_app/cognito_tokens'
        store_or_update_secret(secret_name, secret_value)

    else:
        update_env_var('ACCESS_TOKEN', secret_value['access_token'])
        update_env_var('REFRESH_TOKEN', secret_value['refresh_token'])
        update_env_var('ID_TOKEN', secret_value['id_token'])


# # Example usage
# tokens = get_tokens()
# print("Tokens:", tokens)

# # Example usage
# local_tokens = get_local_tokens()
# print("Local Tokens:", local_tokens)


# Cognito JWT Token Verification
def verify_jwt(token):
    keys_url = f'https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json'
    response = requests.get(keys_url)
    keys = response.json().get('keys')

    try:
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in keys:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
        if rsa_key:
            payload = jwt.decode(token, rsa_key, algorithms=['RS256'], audience=APP_CLIENT_ID)
            return payload
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None


# Function to check if token is expired
def is_token_expired(token):
    try:
        payload = jwt.decode(token, key=None, options={"verify_signature": False})
        exp = payload.get('exp')
        return time.time() > exp
    except Exception as e:
        print(f"Error decoding token: {e}")
        return True  # Assume expired on error


# Middleware for authentication
def authenticate():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None, None

    token = auth_header.split(" ")[1]
    if is_token_expired(token):
        return None, token  # Return the expired token

    payload = verify_jwt(token)
    return payload, None


def refresh_tokens(client_id, client_secret, refresh_token_value, region, user_pool_id):
    url = f'https://bgiuserpoolstaging.auth.us-east-1.amazoncognito.com/oauth2/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token_value
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        result = response.json()
        return {
            'access_token': result['access_token'],
            'id_token': result['id_token'],
            'expires_in': result['expires_in'],
        }
    else:
        print("Error:", response.json())
        return None


# Refresh token if expired
def refresh_token(refresh_token_value):
    client = boto3.client('cognito-idp', region_name=REGION)

    try:
        response = client.initiate_auth(
            ClientId=APP_CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token_value,
                'SECRET_HASH': compute_secret_hash(APP_CLIENT_ID, USERNAME, APP_CLIENT_SECRET)
                # 'SECRET_HASH': APP_CLIENT_SECRET
            }
        )
        return {
            'access_token': response['AuthenticationResult']['AccessToken'],
            'id_token': response['AuthenticationResult']['IdToken'],
            # 'refresh_token': response['AuthenticationResult']['RefreshToken'],
            'expires_in': response['AuthenticationResult']['ExpiresIn']
        }
    except client.exceptions.NotAuthorizedException:
        print("Invalid refresh token provided. It may have expired or been revoked.")
        return None  # Invalid refresh token
    except client.exceptions.ForbiddenException:
        print("Forbidden: Check if the App client is enabled for refresh tokens.")
        return None
    except client.exceptions.InvalidParameterException as e:
        # This exception can indicate that the parameters supplied were invalid
        print(f"Invalid parameter: {e}")
        return None
    except client.exceptions.ResourceNotFoundException as e:
        # This exception indicates that the resource (e.g., user pool) was not found
        print(f"Resource not found: {e}")
        return None
    except client.exceptions.NotAuthorizedException as e:
        # This exception occurs if the refresh token is invalid or expired
        print(f"Not authorized: {e}")
        return None
    except Exception as e:
        # Catch-all for other exceptions, log actual error message
        print(f"An error occurred while refreshing the token: {e}")
        return None


# Decorator for protecting routes
def auth(f):
    def wrapper(*args, **kwargs):
        payload, expired_token = authenticate()

        if not payload:
            # Check if the expired token is available
            if expired_token:
                # Attempt to refresh the token using the refresh token
                refresh_token_value = request.headers.get(
                    'X-Refresh-Token')  # Assume refresh token is sent in a custom header
                if not refresh_token_value:
                    return jsonify({"message": "Unauthorized"}), 401

                new_tokens = refresh_token(refresh_token_value)
                if new_tokens:
                    # Update response with new access token
                    response = f(*args, **kwargs)
                    response.headers['Authorization'] = f"Bearer {new_tokens['access_token']}"
                    return response
                else:
                    return jsonify({"message": "Invalid refresh token"}), 401

            return jsonify({"message": "Unauthorized"}), 401

        request.user = payload  # Store user info in request for later
        return f(*args, **kwargs)  # Call the original function

    wrapper.__name__ = f.__name__  # Preserve function name
    return wrapper


def compute_secret_hash(username, client_id, client_secret):
    key = bytes(client_secret, 'utf-8')
    message = bytes(f'{username}{client_id}', 'utf-8')
    return base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()


def authenticate_user(username, password, client_id, client_secret):
    client = boto3.client('cognito-idp')

    secret_hash = compute_secret_hash(username, client_id, client_secret)

    print(f'XXXXXsecret_hash: {secret_hash}')

    try:
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            }
        )
        return response
    except ClientError as e:
        print(e)
        return None
