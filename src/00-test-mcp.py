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
print(f"Experian Credit Score Result: {credit_result['credit_score']}")

# Test the prompt
print("Testing build_credit_score_prompt:")
prompt = mcp_module.build_credit_score_prompt(score=credit_result['credit_score'])
print(f"Result: {prompt}\n")