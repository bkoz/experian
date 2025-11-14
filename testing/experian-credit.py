import requests
import json
import os
import logging
import dotenv
import logging

dotenv.load_dotenv(".env")
dotenv.dotenv_values()

logging.basicConfig(level=logging.DEBUG)
logging.debug(f'{dotenv.dotenv_values()=}')

    
# --- Experian API Credentials and Configuration ---
# You must replace these placeholder values with your actual credentials from the Experian Developer Portal.
# Note: This is for the sandbox environment.

# Replace with your actual credentials
USERNAME = os.getenv("EXPERIAN_USERNAME")
PASSWORD = os.getenv("EXPERIAN_PASSWORD")
CLIENT_ID = os.getenv("EXPERIAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("EXPERIAN_CLIENT_SECRET")
TOKEN_URL = "https://sandbox-us-api.experian.com/oauth2/v1/token" # Sandbox URL

# curl -X POST https://sandbox-us-api.experian.com/oauth2/v1/token \

headers = {
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded"
}

payload = {
    "grant_type": "password",
    "username": USERNAME,
    "password": PASSWORD,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

try:
    logging.debug(f"Making request to {TOKEN_URL}")
    logging.debug(f"Headers: {headers}")
    logging.debug(f"Payload: {payload}")
    response = requests.post(TOKEN_URL, data=payload, headers=headers)
    logging.debug(f"Response status: {response.status_code}")
    logging.debug(f"Response body: {response.text}")
    response.raise_for_status()
    token_data = response.json()
    access_token = token_data.get("access_token")
    logging.info(f"Successfully obtained access token")
except requests.exceptions.RequestException as e:
    logging.error(f"Error obtaining token: {e}")
    if hasattr(e.response, 'text'):
        logging.error(f"Error details: {e.response.text}")
    access_token = None

import requests
import json

# Assuming 'access_token' was obtained
if access_token:
    # Example: Requesting a consumer credit report
    CREDIT_REPORT_URL = "https://sandbox-us-api.experian.com/v2/consumer/reports"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    request_body = {
        "type": "credit-report",
        "subtype": "standard",
        "consumer": {
            "personalInformation": {
                "name": {
                    "first": "John",
                    "last": "Doe"
                },
                "dateOfBirth": "1980-01-01",
                "socialSecurityNumber": "999999999"
            },
            "addresses": [
                {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "zip": "90210",
                    "addressType": "current"
                }
            ]
        },
        "permissiblePurpose": {
            "type": "ACCOUNT_REVIEW",
            "subtype": "account_review_standard"
        },
        "vendor": {
            "vendorNumber": "1234567"
        },
        "options": {
            "includeFraudShield": True,
            "includeInquiries": True
        }
    }

    try:
        logging.debug(f"Making request to {CREDIT_REPORT_URL}")
        logging.debug(f"Headers: {headers}")
        logging.debug(f"Payload: {json.dumps(request_body, indent=2)}")
        response = requests.post(CREDIT_REPORT_URL, json=request_body, headers=headers)
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Response body: {response.text}")
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        response.raise_for_status()
        report_data = response.json()
        print("\nCredit Report Results:")
        print(json.dumps(report_data, indent=4))
    except requests.exceptions.RequestException as e:
        print(f"\nError requesting credit report: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response Status Code: {e.response.status_code}")
            print(f"Response Headers: {dict(e.response.headers)}")
            print(f"Error details: {e.response.text}")
else:
    print("\nFailed to retrieve credit report - no access token available.")



