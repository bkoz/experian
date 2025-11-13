# MCP Credit Risk Assessment with Experian Integration
## For demonstration purposes only

### Prerequisites
- Linux or Mac
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Experian Developer Sandbox Credentials](https://developer.experian.com/)
- Copy `dot_env` to `.env` and edit as necessary

### Environment Variables
Create an `.env` file (you can copy the example `dot_env`) and set the following:

```console
EXPERIAN_USERNAME="..."
EXPERIAN_PASSWORD="..."
EXPERIAN_CLIENT_ID="..."
EXPERIAN_CLIENT_SECRET="..."
GITHUB_TOKEN='...'
```

### Consumer Credit Report 

These examples call the Experian Developer Consumer Credit Profile Sandbox

> [! NOTE]
> Although they require authentication, these examples make use of Experian's Developer Sandbox
> which do not perform actual credit checks.


### Run the credit risk agent
```bash
uv run src/00-risk-client-mcp.py
```
Example output
```console
============================================================
FINAL RISK ASSESSMENT FROM LLM:
============================================================
### Loan Risk Assessment for Applicant

#### Applicant Information:
- **Name:** Karl E. Daniel
- **Date of Birth:** December 10, 1949
- **SSN:** 123-45-6789 (data retrieved from Experian reporting system)
- **Credit Report Date:** August 6, 2019

---

#### Credit Score Overview:
- **Credit Score:** 783
- **Credit Score Model Indicator:** RC

#### Credit Score Evaluation:
- **Evaluation Code:** P (Likely stands for "Prime" grade, which is considered an excellent credit quality)

#### Score Factors Affecting the Credit Score:
The following factors have impacted the credit score, listed in order of importance:
1. **Code 11 (Most impactful)**
2. **Code 12**
3. **Code 10**
4. **Code 13 (Least impactful)**

(Note: The codes represent Experian-specific credit scoring factors, and their exact definitions can be obtained from Experian documentation. Common examples might include payment history, credit utilization, length of credit history, etc.)

---

#### Risk Assessment Summary:
With a credit score of 783:
1. **Loan Eligibility:** The applicant is highly likely to qualify for most loan products, including unsecured and prime credit loans.
2. **Interest Rate Tier:** Likely to secure loans at the lowest interest rates available due to their excellent credit rating.
3. **Default Risk:** Minimal default risk based on the evaluation and credit score model. The likelihood of timely repayment appears very high.

#### Recommendations:
- No additional credit enhancement (e.g., co-signers or additional collateral) should be necessary given the applicant's stellar creditworthiness.
- Consider offering favorable loan terms, such as lower interest rates or extended payment periods, to capitalize on their strong financial profile.

If further clarification on the credit score factors or additional documentation is required, more detailed information can be requested from the credit reporting agency.

Let me know if any additional details or assessments are needed!
============================================================
```

### Testing and troubleshooting

#### Standalone Example Experian clients

```bash
uv run src/01-experian-business.py
```

```json
{
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
 
2) Example

```bash
uv run src/02-experian-credit-report.py 2> output.json
```


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

#### MCP Server Testing
```bash
uv add mcp[cli] fastmcp
```

```bash
npx modelcontextprotocol/inspector@latest --cli --method=tools/list -- uv run mcp run src/00-experian-mcp-server.py
```

```bash
npx @modelcontextprotocol/inspector@latest --cli --method=tools/call --tool-name=credit_score --tool-arg=ssn="123-456-7890" -- uv run mcp run src/00-experian-mcp-
server.py
```

```bash
npx @modelcontextprotocol/inspector@latest --cli --method=prompts/list -- uv run mcp run src/00-experian-mcp-server.py
```

```bash
npx @modelcontextprotocol/inspector@latest --cli --method=prompts/get --prompt-name=build_credit_score_prompt --prompt-args='credit_report={"ssn":"123"}' -- uv run mcp run src/00-experian-mcp-server.py
```
```json
{
  "description": "Build a prompt for generating a loan risk assessment based on the credit score. \nArgs: \n    credit_report (str): JSON string or dict containing the credit report data.\nReturns: \n    str: The generated prompt.\n",
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "You are a financial assistant. Generate a loan risk assessment for an applicant based on this credit report: {'ssn': '123'}."
      }
    }
  ]
}
```

#### Ollama setup
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:3b
ollama serve
```