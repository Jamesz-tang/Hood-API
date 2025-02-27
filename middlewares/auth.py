import base64
import hashlib
import hmac
import logging
import time

import boto3
import requests
from botocore.exceptions import ClientError
from flask import request, jsonify
from jose import jwt

from utils import secret

logger = logging.getLogger(__name__)


# Cognito JWT Token Verification
def verify_jwt(token):
    cred = secret.get_credentials()

    aws_region = cred['aws_region']
    user_pool_id = cred['user_pool_id']
    client_id = cred['client_id']
    keys_url = f'https://cognito-idp.{aws_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'

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
            payload = jwt.decode(token, rsa_key, algorithms=['RS256'], audience=client_id)
            return payload
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None


# Function to check if token is expired
def is_token_expired(token):
    try:
        payload = jwt.decode(token, key=None, options={"verify_signature": False})
        exp = payload.get('exp')
        return time.time() > exp
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
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
    cred = secret.get_credentials()
    cognito_domain = cred['cognito_domain']

    url = f'{cognito_domain}/oauth2/token'
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
        cred['access_token'] = result['access_token']
        cred['id_token'] = result['id_token']

        # Store credentials
        # secret.store_credentials(cred)

        return {
            'access_token': result['access_token'],
            'id_token': result['id_token'],
            'expires_in': result['expires_in'],
        }
    else:
        logger.error("Error:", response.json())
        return None


def auth(f):
    def wrapper(*args, **kwargs):
        payload, expired_token = authenticate()

        if not payload:
            # Check if the expired token is available
            if expired_token:
                return jsonify({"message": "Token expired"}), 401
                # # Attempt to refresh the token using the refresh token
                # refresh_token_value = request.headers.get(
                #     'X-Refresh-Token')  # Assume refresh token is sent in a custom header
                # if not refresh_token_value:
                #     return jsonify({"message": "Unauthorized"}), 401
                #
                # new_tokens = refresh_token(refresh_token_value)
                # if new_tokens:
                #     # Update response with new access token
                #     response = f(*args, **kwargs)
                #     response.headers['Authorization'] = f"Bearer {new_tokens['access_token']}"
                #     return response
                # else:
                #     return jsonify({"message": "Invalid refresh token"}), 401

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
        logger.error(e)
        return None
