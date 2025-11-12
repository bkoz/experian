import requests
import json
import os
import logging
import dotenv

dotenv.load_dotenv(".env")

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

logging.basicConfig(level=logging.INFO)

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
    logging.debug(f"Access Token: {access_token}")
except requests.exceptions.RequestException as e:
    logging.error(f"Error obtaining token: {e}")
    access_token = None


# Assuming 'access_token' was obtained from the previous step
if access_token:
    logging.info("Obtained Experian access token.")
    # Example: Searching for a business (replace with your specific API endpoint and parameters)
    API_URL = "https://sandbox-us-api.experian.com/businessinformation/businesses/v1/search"
    API_URL = "https://sandbox-us-api.experian.com/businessinformation/businesses/v1/headers"

    # Define query parameters for a GET request (example parameters)

    params = {
        "bin": "807205801",
        "subcode": "0586548"
    }   
    headers = {
        "accept": "application/json",
        "Content-Type" : "application/json",
        "x-comments" : "Test Comments",
        "authorization" : f"Bearer {access_token}" # Use the obtained token
    }
    logging.debug(f'headers = {headers}')

    try:
        response = requests.post(API_URL, data=json.dumps(params), headers=headers)
        response.raise_for_status()
        business_data = response.json()
        # Use json.dumps for pretty printing the JSON response
        logging.info(json.dumps(business_data, indent=4))
    except requests.exceptions.RequestException as e:
        logging.error(f'response = {response}')
        logging.error(f"Error making API request: {e}")
else:
    logging.error("Cannot make API request without an access token.")



