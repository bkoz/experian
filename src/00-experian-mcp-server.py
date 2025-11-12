import logging
import os
import sys
import requests

# Logging setup 
# Configure logging to display the time, file name and line number.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(filename)s:%(lineno)d - %(message)s'
)

from mcp.server.fastmcp import FastMCP

# --- Credentials ---
USERNAME = os.getenv("EXPERIAN_USERNAME")
PASSWORD = os.getenv("EXPERIAN_PASSWORD")
CLIENT_ID = os.getenv("EXPERIAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("EXPERIAN_CLIENT_SECRET")

if USERNAME == None or PASSWORD == None or CLIENT_ID == None or CLIENT_SECRET == None:
    logging.error("Experian USERNAME, PASSWORD, CLIENT_ID or CLIENT_SECRET not set in environment variables. Exiting.")
    exit(1)

sys.path.insert(0, '/workspaces/experian')

TOKEN_URL = "https://sandbox-us-api.experian.com/oauth2/v1/token"  # Sandbox URL

# Create an MCP server
mcp = FastMCP("Experian MCP Server v0.1")

def get_access_token() -> str | None:
    """Obtain OAuth2 token using ROPC flow as required by Experian sandbox."""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    try:
        logging.debug(f"Token request headers: {headers}")
        resp = requests.post(TOKEN_URL, data=payload, headers=headers)
        logging.debug(f"Token response: {resp.status_code} {resp.text}")
        resp.raise_for_status()
        return resp.json().get("access_token")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error obtaining token: {e}")
        if hasattr(e, "response") and getattr(e, "response") is not None:
            logging.error(f"Token error details: {e.response.text}")
        return None

access_token = get_access_token()
if not access_token:
    logging.error("Cannot make API request without an access token.")
    exit(1)

logging.info("Obtained Experian access token.")

@mcp.tool()
def credit_score(ssn: str) -> dict:
    """Fetch credit score for a given SSN from Experian API (mock implementation).
    Args:
        ssn (str): Social Security Number of the applicant.
    Returns:
        dict: A dictionary containing the credit score information.
    """
    return {
        "ssn": ssn,
        "credit_score": 750,
        "report_date": "2024-01-01"
    }

@mcp.prompt()
def build_credit_score_prompt(score: int) -> str:
    """Build a prompt for generating a loan risk assessment based on the credit score. Args: score (int): Returns: str: The generated prompt."""
    return f"You are a financial assistant. Generate a loan risk assessment for an applicant with a credit score of {score}."