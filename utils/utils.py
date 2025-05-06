from google.cloud import secretmanager
from os import getenv

# Initialize the Secrets client
SECRET_CLIENT = secretmanager.SecretManagerServiceClient()
"""
Google Cloud Secret Manager client.

Description:
------------
This client is used to access Google Cloud Secret Manager, allowing retrieval of secrets 
such as passwords, tokens, and other credentials that need to be securely stored.
"""

def get_secret(secret_name: str) -> str:
    """
    Retrieves the value of a secret stored in Google Cloud Secret Manager.

    Args:
        secret_name (str):Name of the secret in Google Cloud Secret Manager.

    Returns:
        str: Value of the requested secret.
    """

    project_id = getenv("GOOGLE_CLOUD_PROJECT")
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    try:
        response = SECRET_CLIENT.access_secret_version(name=name)
    except Exception as e:
        print(f"Error retrieving the secret from GCP: {e}")
        raise Exception(e)
    return response.payload.data.decode('UTF-8')