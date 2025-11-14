# Testing
## For demonstration purposes only

#### Standalone Example Experian clients

```bash
uv run testing/01-experian-business.py
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
uv run testing/02-experian-credit-report.py 2> output.json
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
npx modelcontextprotocol/inspector@latest --cli --method=tools/list -- uv run mcp run src/server.py
```

```bash
npx @modelcontextprotocol/inspector@latest --cli --method=tools/call --tool-name=credit_score --tool-arg=ssn="123-456-7890" -- uv run mcp run src/00-experian-mcp-
server.py
```

```bash
npx @modelcontextprotocol/inspector@latest --cli --method=prompts/list -- uv run mcp run src/server.py
```

```bash
npx @modelcontextprotocol/inspector@latest --cli --method=prompts/get --prompt-name=build_credit_score_prompt --prompt-args='credit_report={"ssn":"123"}' -- uv run mcp run src/server.py
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
