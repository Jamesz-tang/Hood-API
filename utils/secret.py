import json
import os

import boto3


# Function to get the secret name from the environment variables
def get_secret_name():
    """
    Get secret name from environment variables.
    :return:
    """
    env = os.getenv('APP_ENV', 'development')
    return f'/smart-packing/{env}/credentials'


# Function to create or update secret value to secret manager
def store_or_update_secret(secret_name, secret_value):
    """
    Store or update the secret with the given value.
    Example usage:
        secret_name = 'my_app/my_secret'
        secret_value = {
            'user_pool_id': 'your_user_pool_id_value',
            'client_id': 'your_client_id_value',
            'client_secret': 'your_client_secret_value',
            'aws_region': 'your_aws_region',
            'cognito_domain': 'your_cognito_domain_value',
            'user_name': 'your_user_name_',
            'password': 'your_password',
            'access_token': 'your_access_token_value',
            'refresh_token': 'your_refresh_token_value',
            'id_token': 'your_id_token_value'
        }
        store_or_update_secret(secret_name, secret_value)
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
    except client.exceptions.ResourceExistsException:
        # If the secret already exists, update it
        response = client.put_secret_value(
            SecretId=secret_name,
            SecretString=secret_value_json
        )


# Function to update environment variable
def update_env_var(variable_name, value):
    """
    Update the secret with the given value.
    Example usage
        update_env_var('MY_SECRET_KEY', 'new_secret_value')
    :param variable_name:
    :param value:
    :return:
    """
    os.environ[variable_name] = value


def update_local_credentials(secret_name, secret_value):
    update_env_var('USER_POOL_ID', secret_value['user_pool_id'])
    update_env_var('APP_CLIENT_ID', secret_value['client_id'])
    update_env_var('APP_CLIENT_SECRET', secret_value['client_secret'])
    update_env_var('AWS_REGION', secret_value['aws_region'])
    update_env_var('COGNITO_DOMAIN', secret_value['cognito_domain'])
    update_env_var('USERNAME', secret_value['username'])
    update_env_var('PASSWORD', secret_value['password'])
    update_env_var('ACCESS_TOKEN', secret_value['access_token'])
    update_env_var('REFRESH_TOKEN', secret_value['refresh_token'])
    update_env_var('ID_TOKEN', secret_value['id_token'])


# Function to retrieve secret value from secret manager
def retrieve_secret(secret_name):
    """
    Retrieve secret value from secret manager.
    Example usage:
        secret_name = 'my_app/my_secret'
        secret_value = retrieve_secret(secret_name)
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


# Function to get local credentials from environment variables
def get_local_credentials():
    return {
        'user_pool_id': os.getenv('USER_POOL_ID'),
        'client_id': os.getenv('APP_CLIENT_ID'),
        'client_secret': os.getenv('APP_CLIENT_SECRET'),
        'aws_region': os.getenv('AWS_REGION', 'us-east-1'),
        'cognito_domain': os.getenv('COGNITO_DOMAIN'),
        'username': os.getenv('USERNAME'),
        'password': os.getenv('PASSWORD'),
        'access_token': os.getenv('ACCESS_TOKEN'),
        'id_token': os.getenv('ID_TOKEN'),
        'refresh_token': os.getenv('REFRESH_TOKEN'),
    }


# Function to retrieve credentials from secret manager or from environment variables depending on app environment.
def get_credentials():
    """
    Retrieve tokens from secret manager or from environment variables depending on app environment.
    :return:
    """
    env = os.getenv('APP_ENV', 'development')
    if env == 'production' or env == 'staging':
        # Retrieve tokens from AWS Secrets Manager
        client = boto3.client('secretsmanager')
        secret_name = get_secret_name()

        response = client.get_secret_value(SecretId=secret_name)
        secret_value_json = response['SecretString']
        secret_value = json.loads(secret_value_json)

    else:
        # Retrieve tokens from environment variables
        secret_value = get_local_credentials()

    return secret_value


# Function to create or update credentials to secret manager or to environment variables depending on app environment.
def store_credentials(secret_value):
    env = os.getenv('APP_ENV', 'development')

    if env == 'production' or env == 'staging':
        secret_name = get_secret_name()
        store_or_update_secret(secret_name, secret_value)

    else:
        update_local_credentials(secret_value)
