import requests
import json
import os
import dotenv
import logging

dotenv.load_dotenv(".env")
dotenv.dotenv_values()

logging.basicConfig(level=logging.DEBUG)
logging.debug(f'{dotenv.dotenv_values()=}')

    
# --- Experian API Credentials and Configuration ---
# You must replace these placeholder values with your actual credentials from the Experian Developer Portal.
# Note: This is for the sandbox environment.
USERNAME = os.getenv("EXPERIAN_USERNAME")
PASSWORD = os.getenv("EXPERIAN_PASSWORD")
CLIENT_ID = os.getenv("EXPERIAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("EXPERIAN_CLIENT_SECRET")

TOKEN_URL = "https://sandbox-us-api.experian.com/oauth2/v1/token"
FICO_SCORE_URL = "https://sandbox-us-api.experian.com/v1/ficoScore"

def get_access_token(username, password, client_id, client_secret):
    """
    Obtains an OAuth 2.0 Bearer token from the Experian API.
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret
    }

    try:
        logging.debug(f"Making request to {TOKEN_URL}")
        logging.debug(f"Headers: {headers}")
        logging.debug(f"Payload: {payload}")
        response = requests.post(TOKEN_URL, headers=headers, data=payload)
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Response body: {response.text}")
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        token_data = response.json()
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error obtaining token: {e}")
        return None

def perform_credit_check(access_token, consumer_data):
    """
    Makes a request to the FICO score endpoint using the access token.
    """
    if not access_token:
        print("Cannot perform credit check without an access token.")
        return None

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Log request details
        logging.debug(f"Making request to {FICO_SCORE_URL}")
        logging.debug(f"Headers: {headers}")
        logging.debug(f"Payload: {json.dumps(consumer_data, indent=2)}")
        
        response = requests.post(FICO_SCORE_URL, headers=headers, json=consumer_data)
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Response body: {response.text}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error performing credit check: {e}")
        if hasattr(e.response, 'text'):
            print(f"Error details: {e.response.text}")
        return None

if __name__ == "__main__":
    # --- Sample Consumer Data (for sandbox testing) ---
    # The actual data required will be specified in the Experian API documentation for this specific endpoint.
    sample_consumer_data = {
        "firstName": "John",
        "lastName": "Doe",
        "ssn": "999999999",
        "dob": "1980-01-01",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zip": "90210",
        "reportType": "fico8",
        "purpose": "31",
        "subcode": "1234567"
    }

    # 1. Get the access token
    logging.debug(f"Credentials loaded - USERNAME: {'set' if USERNAME else 'not set'}, PASSWORD: {'set' if PASSWORD else 'not set'}, CLIENT_ID: {'set' if CLIENT_ID else 'not set'}, CLIENT_SECRET: {'set' if CLIENT_SECRET else 'not set'}")
    
    token = get_access_token(USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET)

    if token:
        logging.info("Successfully obtained access token.")
        
        # 2. Perform the credit check
        credit_report = perform_credit_check(token, sample_consumer_data)
        
        if credit_report:
            print("\nCredit Check Results:")
            # Pretty print the JSON response
            print(json.dumps(credit_report, indent=4))
        else:
            print("\nFailed to retrieve credit report.")
    else:
        print("Failed to obtain access token. Please check your credentials.")



