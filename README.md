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
uv run src/client.py
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

### Code Summary

The `src/client.py` script acts as a test client for an Experian MCP (Microservice Context Protocol) server, supporting both HTTP and standard I/O (stdio) transport methods. It integrates with OpenAI's API for language model interactions to perform tasks such as financial risk assessment.

### Key Components and Functionalities:

*   **`to_llm_tool(tool)`**: A utility function that converts an MCP tool's definition into a schema compatible with OpenAI's function calling.
*   **`HttpMcpClient`**: An asynchronous class for handling JSON-RPC over HTTP communication with the MCP server. It includes methods for session initialization, listing available tools and prompts, and executing tools and prompts.
*   **`parse_args()`**: Responsible for parsing command-line arguments to configure the client's transport method (`stdio` or `http`) and the server URL.
*   **`main()`**: The primary entry point, which dispatches execution to either `run_http_client` or `run_client_session` based on the chosen transport.
*   **`run_http_client(url)`**: Manages client operations over HTTP. It initializes an MCP session, retrieves a list of available tools, invokes the `credit_score` tool with sample data, processes the credit report, and then engages an LLM with a prompt for financial risk assessment, incorporating the tool outputs.
*   **`call_llm_and_process(...)`**: An asynchronous function that orchestrates interactions with the OpenAI LLM. It sends prompts and tools to the LLM. If the LLM suggests a tool call, this function executes the tool via the MCP client, feeds the result back to the LLM, and finally generates a comprehensive risk assessment.
*   **`run_client_session(read, write)`**: Handles client operations using stdio transport. It mirrors the functionality of `run_http_client`, including session initialization, tool listing, `credit_score` tool invocation, and LLM-driven risk assessment using prompts retrieved from the MCP server.

In summary, `src/client.py` serves as a demonstration of connecting to an MCP server, discovering its services, executing its tools, and integrating these capabilities into a simple, yet powerful, LLM-based agentic workflow for tasks like generating detailed financial risk assessments.