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

