import requests
import json
import os
import logging

# Replace with your actual credentials
USERNAME = os.getenv("EXPERIAN_USERNAME")
PASSWORD = os.getenv("EXPERIAN_PASSWORD")
CLIENT_ID = os.getenv("EXPERIAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("EXPERIAN_CLIENT_SECRET")
TOKEN_URL = "https://sandbox-us-api.experian.com/oauth2/v1/token" # Sandbox URL

payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}


print(f'{payload=}')

# curl -X POST https://sandbox-us-api.experian.com/oauth2/v1/token \

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Grant_type": "password",
}

try:
    response = requests.post(TOKEN_URL, data=json.dumps(payload), headers=headers)
    response.raise_for_status() # Raise an exception for bad status codes
    token_data = response.json()
    access_token = token_data.get("access_token")
    print(f"Access Token: {access_token}")
except requests.exceptions.RequestException as e:
    print(f"Error obtaining token: {e}")
    access_token = None

import requests
import json

# Assuming 'access_token' was obtained
if access_token:
    # Example: Requesting a consumer credit report (replace with actual endpoint and schema)
    CREDIT_REPORT_URL = "https://sandbox-us-api.experian.com/consumer/services/credit/v1/fico-score"


    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    request_body = {"ssn": "123-45-6789"}
    # data = json.dumps(body).encode('utf-8')

    try:
        response = requests.post(CREDIT_REPORT_URL, data=json.dumps(request_body), headers=headers)
        response.raise_for_status()
        report_data = response.json()
        print(json.dumps(report_data, indent=4))
    except requests.exceptions.RequestException as e:
        print(f"Error requesting credit report: {e}")



