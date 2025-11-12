from mcp.server.fastmcp import FastMCP


# Create an MCP server
mcp = FastMCP("Experian MCP Server v0.1")

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