# experian

### Prerequisites
- Linux or Mac
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Experian Developer Credentials](https://developer.experian.com/)
- Copy `dot_env` to `.env` and edit as necessary


### Example Experian clients

Only this example is currently working.

```bash
uv run src/01-experian-business.py
```

```console
INFO:root:Obtained Experian access token.
INFO:root:{
    "requestId": "rrt-02dce8480b81b09df-c-ea-1454121-44360798-1",
    "success": true,
    "results": {
        "bin": "796744203",
        "businessName": "EXPERIAN INFORMATION SOLUTIONS, INC",
        "address": {
            "street": "475 ANTON BLVD",
            "city": "COSTA MESA",
            "state": "CA",
            "zip": "92626",
            "zipExtension": "7037"
        },
        "phone": "+17148307000",
        "taxId": "133015410",
        "websiteUrl": "http://www.experian.com",
        "legalBusinessName": "EXPERIAN INFORMATION SOLUTIONS, INC.",
        "dbaNames": null,
        "customerDisputeIndicator": false
    }
}
```
 
### Consumer Credit Report (sandbox)

This example calls the Experian Consumer Credit Profile v2 credit report endpoint. It requires extra org identifiers in addition to your OAuth credentials.

1) Create an `.env` file (you can copy from `dot_env`) and set the following:

```
EXPERIAN_USERNAME="..."
EXPERIAN_PASSWORD="..."
EXPERIAN_CLIENT_ID="..."
EXPERIAN_CLIENT_SECRET="..."

# Required for the credit-profile v2 API
EXPERIAN_COMPANY_ID="<your company id>"
EXPERIAN_SUBSCRIBER_CODE="<your subscriber code>"
```

2) Run:

```bash
uv run src/experian-credit-report.py
```

If `EXPERIAN_COMPANY_ID` is missing, the script will fail fast with a helpful error (the API requires `companyId` as a header). If the request still returns a 400, double‑check your permissible purpose, company/subscriber codes, and that your sandbox account is entitled for Consumer Credit Profile.

Output
```bash
cat output.json |jq .creditProfile[0].riskModel
```

```json
[
  {
    "evaluation": "P",
    "modelIndicator": "RC",
    "score": "0783",
    "scoreFactors": [
      {
        "importance": "1",
        "code": "11"
      },
      {
        "importance": "2",
        "code": "12"
      },
      {
        "importance": "3",
        "code": "10"
      },
      {
        "importance": "4",
        "code": "13"
      }
    ]
  }
]
```
