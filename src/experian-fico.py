import requests
import json
import os

# --- Experian API Credentials and Configuration ---
# You must replace these placeholder values with your actual credentials from the Experian Developer Portal.
# Note: This is for the sandbox environment.
USERNAME = os.getenv("EXPERIAN_USERNAME")
PASSWORD = os.getenv("EXPERIAN_PASSWORD")
CLIENT_ID = os.getenv("EXPERIAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("EXPERIAN_CLIENT_SECRET")

TOKEN_URL = "https://sandbox-us-api.experian.com/oauth2/v1/token"
FICO_SCORE_URL = "https://sandbox-us-api.experian.com/consumer/services/credit/v1/fico-score"

def get_access_token(username, password, client_id, client_secret):
    """
    Obtains an OAuth 2.0 Bearer token from the Experian API.
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "grant_type": "password"
    }
    payload = {
        "username": username,
        "password": password,
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        response = requests.post(TOKEN_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        token_data = response.json()
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining token: {e}")
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
        # The consumer_data payload needs to follow the specific schema required by the API.
        # This example uses common, but potentially non-exhaustive, fields.
        response = requests.post(FICO_SCORE_URL, headers=headers, data=json.dumps(consumer_data))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error performing credit check: {e}")
        return None

if __name__ == "__main__":
    # --- Sample Consumer Data (for sandbox testing) ---
    # The actual data required will be specified in the Experian API documentation for this specific endpoint.
    sample_consumer_data = {
        "firstName": "John",
        "lastName": "Doe",
        "dateOfBirth": "1980-01-01", 
        "ssn": "999999999", # Sandbox test SSN
        "street1": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zipCode": "90210"
    }

    # 1. Get the access token
    token = get_access_token(USERNAME, PASSWORD, CLIENT_ID, CLIENT_SECRET)

    if token:
        print("Successfully obtained access token.")
        
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



