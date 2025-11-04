import requests
import json
import os
import logging
import dotenv

# Load environment from .env and fallback to dot_env if present
dotenv.load_dotenv(".env")
dotenv.load_dotenv("dot_env")

# Logging setup
logging.basicConfig(level=logging.INFO)

# --- Credentials ---
USERNAME = os.getenv("EXPERIAN_USERNAME")
PASSWORD = os.getenv("EXPERIAN_PASSWORD")
CLIENT_ID = os.getenv("EXPERIAN_CLIENT_ID")
CLIENT_SECRET = os.getenv("EXPERIAN_CLIENT_SECRET")

# --- Consumer Credit required org identifiers ---
COMPANY_ID = os.getenv("EXPERIAN_COMPANY_ID")  # Required for consumer credit API
# Many docs refer to "subscriberCode"; some headers use "Subcode". Support both env names.
SUBSCRIBER_CODE = (
    os.getenv("EXPERIAN_SUBSCRIBER_CODE")
    or os.getenv("EXPERIAN_SUBCODE")
    or os.getenv("EXPERIAN_SUB_CODE")
)

CLIENT_REFERENCE_ID = os.getenv("EXPERIAN_CLIENT_REFERENCE_ID", "SBMYSQL")

TOKEN_URL = "https://sandbox-us-api.experian.com/oauth2/v1/token"  # Sandbox URL


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
        logging.debug(f"Token payload: {payload}")
        resp = requests.post(TOKEN_URL, data=payload, headers=headers)
        logging.debug(f"Token response: {resp.status_code} {resp.text}")
        resp.raise_for_status()
        return resp.json().get("access_token")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error obtaining token: {e}")
        if hasattr(e, "response") and getattr(e, "response") is not None:
            logging.error(f"Token error details: {e.response.text}")
        return None


def build_credit_report_request() -> dict:
    """Build request body matching Experian Credit Profile v2 schema.

    Fields intentionally minimal for sandbox; adjust as needed.
    """
    # Basic consumer identity for sandbox
    consumer_pii = {
        "names": [
            {
                "firstName": "John",
                "surname": "Doe",
            }
        ],
        "dob": {
            "dob": "1980-01-01",
        },
        "ssn": "999999999",
        "addresses": [
            {
                "street": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "zipCode": "90210",
                "type": "current",
            }
        ],
    }

    requestor = {}
    if SUBSCRIBER_CODE:
        requestor["subscriberCode"] = SUBSCRIBER_CODE
    if COMPANY_ID:
        requestor["companyId"] = COMPANY_ID

    body = {
        "permissiblePurpose": {
            # ACCOUNT_REVIEW is a common sandbox purpose; adjust per your agreement
            "type": "ACCOUNT_REVIEW",
        },
        "requestor": requestor,
        "consumerPii": consumer_pii,
        # Optional: include client reference for traceability
        "clientReferenceId": CLIENT_REFERENCE_ID,
    }
    body = {"consumerPii": { "primaryApplicant": { "name": { "lastName": "CANN", "firstName": "JOHN", "middleName": "N" }, "dob": { "dob": "1955" }, "ssn": { "ssn": "111111111" }, "currentAddress": { "line1": "510 MONDRE ST", "city": "MICHIGAN CITY", "state": "IN", "zipCode": "46360" } } }, "requestor": { "subscriberCode": "2222222" }, "permissiblePurpose": { "type": "08" }, "resellerInfo": { "endUserName": "CPAPIV2TC21" }, "vendorData": { "vendorNumber": "072", "vendorVersion": "V1.29" }, "addOns": { "directCheck": "", "demographics": "Only Phone", "clarityEarlyRiskScore": "Y", "liftPremium": "Y", "clarityData": { "clarityAccountId": "0000000", "clarityLocationId": "000000", "clarityControlFileName": "test_file", "clarityControlFileVersion": "0000000" }, "renterRiskScore": "N", "rentBureauData": { "primaryApplRentBureauFreezePin": "1234", "secondaryApplRentBureauFreezePin": "112233" }, "riskModels": { "modelIndicator": [ "" ], "scorePercentile": "" }, "summaries": { "summaryType": [ "" ] }, "fraudShield": "Y", "mla": "", "ofacmsg": "", "consumerIdentCheck": { "getUniqueConsumerIdentifier": "" }, "joint": "", "paymentHistory84": "", "syntheticId": "N", "taxRefundLoan": "Y", "sureProfile": "Y", "incomeAndEmploymentReport": "Y", "incomeAndEmploymentReportData": { "verifierName": "Experian", "reportType": "ExpVerify-Plus" } }, "customOptions": { "optionId": [ "COADEX" ] } }

    return body


def main() -> None:
    # Validate presence of minimum credentials
    missing = [
        name
        for name, val in [
            ("EXPERIAN_USERNAME", USERNAME),
            ("EXPERIAN_PASSWORD", PASSWORD),
            ("EXPERIAN_CLIENT_ID", CLIENT_ID),
            ("EXPERIAN_CLIENT_SECRET", CLIENT_SECRET),
        ]
        if not val
    ]
    if missing:
        logging.error(
            "Missing required env vars: %s. Create an .env (or dot_env) file with these values.",
            ", ".join(missing),
        )
    logging.info(f"Using COMPANY_ID: {COMPANY_ID or '(not set)'}")
    logging.info(f"Using SUBSCRIBER_CODE: {SUBSCRIBER_CODE or '(not set)'}")

    access_token = get_access_token()
    if not access_token:
        logging.error("Cannot make API request without an access token.")
        return

    logging.info("Obtained Experian access token.")

    API_URL = (
        "https://sandbox-us-api.experian.com/consumerservices/credit-profile/v2/credit-report"
    )
    body = build_credit_report_request()

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        # Some integrations pass Subcode as a header; we include it if provided
        **({"Subcode": SUBSCRIBER_CODE} if SUBSCRIBER_CODE else {}),
        "Authorization": f"Bearer {access_token}",
    }
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
        logging.info(json.dumps(data, indent=4))
    except requests.exceptions.RequestException as e:
        # Log as much context as possible for debugging
        logging.error(f"response = {response}")
        logging.error(f"Response body: {getattr(response, 'text', '')}")
        logging.error(f"Error making API request: {e}")


if __name__ == "__main__":
    main()



