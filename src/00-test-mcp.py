#!/usr/bin/env python3
"""Test script for the Experian MCP server."""

import sys
import os
import logging
import requests

# Import the server module
import importlib.util
spec = importlib.util.spec_from_file_location("mcp_server", "/workspaces/experian/src/00-experian-mcp-server.py")
mcp_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_module)

# Test the tool
print("Testing credit_score tool:")
credit_result = mcp_module.credit_score(ssn="123-45-6789")
score = credit_result.get('credit_score_info', {}).get('score', 0)
print(f"Experian Credit Score Result: {score}")
print(f"Consumer Name: {credit_result.get('consumer_name', {}).get('first_name', '')} {credit_result.get('consumer_name', {}).get('last_name', '')}")
print(f"Date of Birth: {credit_result.get('date_of_birth', '')}")
print(f"Report Date: {credit_result.get('report_date', '')}")
print(f"Model Indicator: {credit_result.get('credit_score_info', {}).get('model_indicator', '')}")
print(f"Evaluation: {credit_result.get('credit_score_info', {}).get('evaluation', '')}")
print(f"Score Factors: {credit_result.get('credit_score_info', {}).get('score_factors', [])}")


# Test the prompt
print("\nTesting build_credit_score_prompt:")
prompt = mcp_module.build_credit_score_prompt(credit_report = credit_result)
print(f"Result: {prompt}\n")

# Test the prompt using an llm served by Ollama
print("Testing build_credit_score_prompt with Ollama LLM:")
ollama_url = "http://localhost:11434"
ollama_payload = {
    "model": "llama3.2:3b",
    "prompt": prompt,
    "stream": False,  # Disable streaming to get a single JSON response
    "options": {
        "num_predict": 500,
        "temperature": 0.7
    }
}
response = requests.post(f"{ollama_url}/api/generate", json=ollama_payload)
if response.status_code == 200:
    llm_result = response.json()
    print(f"LLM Response: {llm_result.get('response', '')}")
else:
    print(f"Error: {response.status_code} - {response.text}")       

