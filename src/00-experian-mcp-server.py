import logging
import os
import sys
import requests
import json

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

def build_credit_report_request() -> dict:
    """Build request body matching Experian Credit Profile v2 schema.
    Fields intentionally minimal for sandbox; adjust as needed.
    """

    # requestor = {}
    # if SUBSCRIBER_CODE:
    #     requestor["subscriberCode"] = SUBSCRIBER_CODE
    # if COMPANY_ID:
    #     requestor["companyId"] = COMPANY_ID

    body = json.load(open("data/rent.json"))

    return body

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
    API_URL = (
        "https://sandbox-us-api.experian.com/consumerservices/credit-profile/v2/credit-report"
    )
    body = build_credit_report_request()

    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}',
            'accept': 'application/json',
            'clientReferenceId':'SBMYSQL'
    }

    logging.debug(f"Request headers: {headers}")
    logging.debug(f"Request body: {json.dumps(body, indent=2)}")

    try:
        response = requests.post(API_URL, json=body, headers=headers)
        logging.debug(f"Response status: {response.status_code}")
        logging.debug(f"Response body: {response.text}")
        response.raise_for_status()
        data = response.json()
        
        # Parse and return relevant credit score info from the data
        credit_profile = data.get("creditProfile", [{}])[0]
        
        # Extract consumer identity
        consumer_identity = credit_profile.get("consumerIdentity", {})
        dob = consumer_identity.get("dob", {})
        names = consumer_identity.get("name", [{}])
        primary_name = names[0] if names else {}
        
        # Extract header record for report date
        header = credit_profile.get("headerRecord", [{}])[0]
        report_date = header.get("y2kReportedDate", header.get("reportDate", ""))
        
        # Extract risk model (credit score)
        risk_models = credit_profile.get("riskModel", [])
        score_info = {}
        if risk_models:
            risk_model = risk_models[0]
            score_info = {
                "score": int(risk_model.get("score", "0")),
                "model_indicator": risk_model.get("modelIndicator", ""),
                "evaluation": risk_model.get("evaluation", ""),
                "score_factors": [
                    {
                        "code": factor.get("code", ""),
                        "importance": factor.get("importance", "")
                    }
                    for factor in risk_model.get("scoreFactors", [])
                ]
            }
        
        # Extract SSN
        ssn_records = credit_profile.get("ssn", [{}])
        ssn_number = ssn_records[0].get("number", ssn) if ssn_records else ssn
        
        result = {
            "ssn": ssn_number,
            "consumer_name": {
                "first_name": primary_name.get("firstName", ""),
                "middle_name": primary_name.get("middleName", ""),
                "last_name": primary_name.get("surname", "")
            },
            "date_of_birth": f"{dob.get('month', '')}/{dob.get('day', '')}/{dob.get('year', '')}",
            "report_date": report_date,
            "credit_score_info": score_info
        }

        logging.debug(json.dumps(result, indent=4))
        return result
        
    except requests.exceptions.RequestException as e:
        # Log as much context as possible for debugging
        logging.error(f"response = {response}")
        logging.error(f"Response body: {getattr(response, 'text', '')}")
        logging.error(f"Error making API request: {e}")
        return {
            "error": str(e),
            "ssn": ssn
        }

@mcp.prompt()
def build_credit_score_prompt(credit_report: str) -> str:
    """Build a prompt for generating a loan risk assessment based on the credit score. 
    Args: 
        credit_report (str): JSON string or dict containing the credit report data.
    Returns: 
        str: The generated prompt.
    """
    # Parse JSON string if needed
    if isinstance(credit_report, str):
        try:
            credit_report_data = json.loads(credit_report)
        except json.JSONDecodeError:
            credit_report_data = credit_report
    else:
        credit_report_data = credit_report
    
    return f"You are a financial assistant. Generate a loan risk assessment for an applicant based on this credit report: {credit_report_data}."