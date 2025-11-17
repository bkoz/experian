#!/usr/bin/env python3
"""Test script for the Experian MCP server using FastMCP client."""

import asyncio
import sys
import os
import logging
import json
import argparse
import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI


logging.basicConfig(level=logging.INFO)

def to_llm_tool(tool) -> dict:
    """Convert MCP tool to LLM tool schema."""
    tool_schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"]
            }
        }
    }
    return tool_schema

def call_llm(prompt, functions):
    token = os.environ["GITHUB_TOKEN"]
    endpoint = "https://models.github.ai/inference"

    model_name = "gpt-4o"
    model_name = "gpt-4.1"

    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    print("CALLING LLM")
    response = client.chat.completions.create(
        messages=[
            {
            "role": "system",
            "content": "You are a helpful assistant.",
            },
            {
            "role": "user",
            "content": prompt,
            },
        ],
        model=model_name,
        tools = functions,
        # Optional parameters
        temperature=1.,
        max_tokens=1000,
        top_p=1.    
    )

    # .content if we want just see the text response 
    response_message = response.choices[0].message
    
    functions_to_call = []

    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            # print("TOOL: ", tool_call)
            name = tool_call.function.name
            logging("TOOL NAME: ", name)
            args = json.loads(tool_call.function.arguments)
            functions_to_call.append({ "name": name, "args": args })

    return functions_to_call

class HttpMcpClient:
    """Simple HTTP client for MCP JSON-RPC over HTTP."""
    
    def __init__(self, url: str):
        self.url = url
        self.client = httpx.AsyncClient()
        self.request_id = 0
    
    async def close(self):
        await self.client.aclose()
    
    async def call(self, method: str, params: dict = None) -> dict:
        """Make a JSON-RPC call to the MCP server."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        logging.debug(f"Sending request: {json.dumps(request, indent=2)}")
        
        response = await self.client.post(self.url, json=request)
        response.raise_for_status()
        
        result = response.json()
        logging.debug(f"Received response: {json.dumps(result, indent=2)}")
        
        if "error" in result:
            raise Exception(f"MCP error: {result['error']}")
        
        return result.get("result", {})
    
    async def initialize(self):
        """Initialize the MCP session."""
        return await self.call("initialize", {})
    
    async def list_tools(self):
        """List available tools."""
        result = await self.call("tools/list", {})
        return result.get("tools", [])
    
    async def call_tool(self, name: str, arguments: dict):
        """Call a tool."""
        result = await self.call("tools/call", {"name": name, "arguments": arguments})
        return result
    
    async def list_prompts(self):
        """List available prompts."""
        result = await self.call("prompts/list", {})
        return result.get("prompts", [])
    
    async def get_prompt(self, name: str, arguments: dict):
        """Get a prompt."""
        result = await self.call("prompts/get", {"name": name, "arguments": arguments})
        return result

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Experian MCP Client')
    parser.add_argument(
        '--transport',
        type=str,
        choices=['stdio', 'http'],
        default='stdio',
        help='Transport type: stdio (default) or http'
    )
    parser.add_argument(
        '--url',
        type=str,
        default='http://localhost:8000/mcp',
        help='URL for HTTP transport (default: http://localhost:8000/mcp)'
    )
    return parser.parse_args()

async def main():
    """Main test function."""
    args = parse_args()
    
    if args.transport == 'http':
        # Use HTTP transport
        logging.info(f"Connecting to MCP server via HTTP at {args.url}")
        await run_http_client(args.url)
    else:
        # Use stdio transport
        logging.info("Connecting to MCP server via stdio")
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "src/server.py"],
            env=os.environ.copy()
        )
        
        async with stdio_client(server_params) as (read, write):
            await run_client_session(read, write)

async def run_http_client(url: str):
    """Run the client with HTTP transport."""
    client = HttpMcpClient(url)
    
    try:
        # Initialize
        await client.initialize()
        
        # Test MCP server
        available_tools = []
        tools = await client.list_tools()
        logging.debug(f"Available tools: {[tool['name'] for tool in tools]}\n")
        logging.debug("Tools details:")
        for tool in tools:
            logging.debug(f"- {tool['name']}: {tool['description']}")
            # Convert to LLM tool format
            tool_schema = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "type": "function",
                    "parameters": tool["inputSchema"]
                }
            }
            available_tools.append(tool_schema)
        
        logging.debug(f'Available tools converted to LLM schema: {available_tools}\n')

        # Test the credit_score tool
        logging.debug("Testing credit_score tool:")
        result = await client.call_tool("credit_score", {"ssn": "123-45-6789"})
        
        # Parse the result
        credit_result = json.loads(result["content"][0]["text"])
        
        score = credit_result.get('credit_score_info', {}).get('score', 0)
        logging.debug(f"Experian Credit Score Result: {score}")
        logging.debug(f"Consumer Name: {credit_result.get('consumer_name', {}).get('first_name', '')} {credit_result.get('consumer_name', {}).get('last_name', '')}")
        logging.debug(f"Date of Birth: {credit_result.get('date_of_birth', '')}")
        logging.debug(f"Report Date: {credit_result.get('report_date', '')}")
        logging.debug(f"Model Indicator: {credit_result.get('credit_score_info', {}).get('model_indicator', '')}")
        logging.debug(f"Evaluation: {credit_result.get('credit_score_info', {}).get('evaluation', '')}")
        logging.debug(f"Score Factors: {credit_result.get('credit_score_info', {}).get('score_factors', [])}")
        
        # Test the prompt
        logging.debug("Testing build_credit_score_prompt:")
        prompts = await client.list_prompts()
        logging.info(f"Available prompts: {[p['name'] for p in prompts]}")
        
        # Note: The HTTP server doesn't implement prompts/get, so we'll create the prompt directly
        prompt = "You are a financial loan officer assistant. Generate an extensive loan risk assessment for this applicant given a SSN of 123-45-6789."
        logging.debug(f"Using prompt: {prompt}\n")
        
        # Call LLM with the prompt and available tools
        await call_llm_and_process(prompt, available_tools, client, credit_result)
        
    finally:
        await client.close()

async def call_llm_and_process(prompt: str, available_tools: list, mcp_client, credit_result: dict):
    """Call LLM and process the response with tool calls."""
    token = os.environ["GITHUB_TOKEN"]
    endpoint = "https://models.github.ai/inference"
    model_name = "gpt-4o"
    model_name = "gpt-4.1"
    
    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )
    
    messages = [
        {
            "role": "system",
            "content": "You are a helpful financial assistant that generates loan risk assessments based on credit score information.",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]
    
    print("CALLING LLM")
    response = client.chat.completions.create(
        messages=messages,
        model=model_name,
        tools=available_tools,
        temperature=1.,
        max_tokens=1000,
        top_p=1.    
    )
    
    response_message = response.choices[0].message
    
    # Check if the LLM wants to call tools
    if response_message.tool_calls:
        logging.info("Calling tools from LLM result:")
        
        # Add the assistant's response to messages
        messages.append(response_message)
        
        # Execute each tool call
        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            logging.debug(f"Calling tool: {tool_name}, arguments: {tool_args}")
            
            # Call the MCP tool
            if isinstance(mcp_client, HttpMcpClient):
                result = await mcp_client.call_tool(tool_name, arguments=tool_args)
                tool_result = result["content"][0]["text"]
            else:
                result = await mcp_client.call_tool(tool_name, arguments=tool_args)
                tool_result = result.content[0].text
            
            logging.debug(f"Tool result: {tool_result}\n")
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            })
        
        # Call LLM again with tool results to generate final assessment
        logging.info("Calling LLM again with tool results to generate risk assessment...")
        final_response = client.chat.completions.create(
            messages=messages,
            model=model_name,
            tools=available_tools,
            temperature=1.,
            max_tokens=1000,
            top_p=1.    
        )
        
        final_message = final_response.choices[0].message.content
        print("\n" + "="*60)
        print("FINAL RISK ASSESSMENT FROM LLM:")
        print("="*60)
        print(final_message)
        print("="*60)
    else:
        print("No tool calls found in LLM response")
        if response_message.content:
            print(f"LLM response: {response_message.content}")

async def run_client_session(read, write):
    """Run the client session with the given read/write streams."""
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Test MCP server
        available_tools = []
        tools = await session.list_tools()
        logging.debug(f"Available tools: {[tool.name for tool in tools.tools]}\n")
        logging.debug("Tools details:")
        for tool in tools.tools:
            logging.debug(f"- {tool.name}: {tool.description} tool input schema: {tool.inputSchema['properties']}")
            available_tools.append(to_llm_tool(tool))
        
        logging.debug(f'Available tools converted to LLM schema: {available_tools}\n')

        # Test the credit_score tool
        logging.debug("Testing credit_score tool:")
        result = await session.call_tool("credit_score", {"ssn": "123-45-6789"})
        
        # Parse the result
        credit_result = json.loads(result.content[0].text)
        
        score = credit_result.get('credit_score_info', {}).get('score', 0)
        logging.debug(f"Experian Credit Score Result: {score}")
        logging.debug(f"Consumer Name: {credit_result.get('consumer_name', {}).get('first_name', '')} {credit_result.get('consumer_name', {}).get('last_name', '')}")
        logging.debug(f"Date of Birth: {credit_result.get('date_of_birth', '')}")
        logging.debug(f"Report Date: {credit_result.get('report_date', '')}")
        logging.debug(f"Model Indicator: {credit_result.get('credit_score_info', {}).get('model_indicator', '')}")
        logging.debug(f"Evaluation: {credit_result.get('credit_score_info', {}).get('evaluation', '')}")
        logging.debug(f"Score Factors: {credit_result.get('credit_score_info', {}).get('score_factors', [])}")
        
        # Test the prompt
        logging.debug("Testing build_credit_score_prompt:")
        prompts = await session.list_prompts()
        logging.info(f"Available prompts: {[p.name for p in prompts.prompts]}")
        
        prompt_result = await session.get_prompt("build_credit_score_prompt", {"credit_report": json.dumps(credit_result)})
        prompt = prompt_result.messages[0].content.text
        logging.debug(f"Result: {prompt}\n")
        
        # Call LLM with the prompt and available tools
        await call_llm_and_process(prompt, available_tools, session, credit_result)

async def main_async():
    """Async entry point."""
    await main()

if __name__ == "__main__":
    asyncio.run(main())

