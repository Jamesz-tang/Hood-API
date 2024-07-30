import base64
import hashlib
import hmac
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


# Refresh token if expired
def refresh_token(refresh_token):
    client = boto3.client('cognito-idp', region_name=REGION)

    try:
        response = client.initiate_auth(
            ClientId=APP_CLIENT_ID,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token,
                'SECRET_HASH': APP_CLIENT_SECRET  # Include if app client has a secret
            }
        )
        return {
            'access_token': response['AuthenticationResult']['AccessToken'],
            'id_token': response['AuthenticationResult']['IdToken'],
            'refresh_token': response['AuthenticationResult']['RefreshToken'],
            'expires_in': response['AuthenticationResult']['ExpiresIn']
        }
    except client.exceptions.NotAuthorizedException:
        return None  # Invalid refresh token
    except Exception as e:
        print(f"Error refreshing token: {e}")
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


def authenticate_user(username, password, client_id, secret_hash):
    client = boto3.client('cognito-idp')

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


def compute_secret_hash(client_id, username, client_secret):
    key = bytes(client_secret, 'utf-8')
    message = bytes(f'{username}{client_id}', 'utf-8')
    return base64.b64encode(hmac.new(key, message, digestmod=hashlib.sha256).digest()).decode()

