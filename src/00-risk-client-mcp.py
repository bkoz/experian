#!/usr/bin/env python3
"""Test script for the Experian MCP server using FastMCP client."""

import asyncio
import sys
import os
import logging
import requests
import json
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

async def test_mcp_server():
    """Test the MCP server using FastMCP client."""
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "src/00-experian-mcp-server.py"],
        env=os.environ.copy()  # Pass current environment variables to subprocess
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            available_tools = []

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}\n")
            print("Tools details:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description} tool input schema: {tool.inputSchema['properties']}")
                available_tools.append(to_llm_tool(tool))
            
            print(f'Available tools converted to LLM schema: {available_tools}\n')

            # Test the credit_score tool
            print("Testing credit_score tool:")
            result = await session.call_tool("credit_score", {"ssn": "123-45-6789"})
            
            # Parse the result
            import json
            credit_result = json.loads(result.content[0].text)
            
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
            prompts = await session.list_prompts()
            print(f"Available prompts: {[p.name for p in prompts.prompts]}")
            
            prompt_result = await session.get_prompt("build_credit_score_prompt", {"credit_report": json.dumps(credit_result)})
            prompt = prompt_result.messages[0].content.text
            print(f"Result: {prompt}\n")
            
            return session, available_tools, prompt, credit_result
def call_llm(prompt, functions):
    token = os.environ["GITHUB_TOKEN"]
    endpoint = "https://models.github.ai/inference"

    model_name = "gpt-4o"

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
            print("TOOL NAME: ", name)
            args = json.loads(tool_call.function.arguments)
            functions_to_call.append({ "name": name, "args": args })

    return functions_to_call

async def main():
    """Main test function."""
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "src/00-experian-mcp-server.py"],
        env=os.environ.copy()
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Test MCP server
            available_tools = []
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}\n")
            print("Tools details:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description} tool input schema: {tool.inputSchema['properties']}")
                available_tools.append(to_llm_tool(tool))
            
            print(f'Available tools converted to LLM schema: {available_tools}\n')

            # Test the credit_score tool
            print("Testing credit_score tool:")
            result = await session.call_tool("credit_score", {"ssn": "123-45-6789"})
            
            # Parse the result
            credit_result = json.loads(result.content[0].text)
            
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
            prompts = await session.list_prompts()
            print(f"Available prompts: {[p.name for p in prompts.prompts]}")
            
            prompt_result = await session.get_prompt("build_credit_score_prompt", {"credit_report": json.dumps(credit_result)})
            prompt = prompt_result.messages[0].content.text
            print(f"Result: {prompt}\n")
            
            # Call LLM with the prompt and available tools
            token = os.environ["GITHUB_TOKEN"]
            endpoint = "https://models.github.ai/inference"
            model_name = "gpt-4o"
            
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
                print("\nCalling tools from LLM result:")
                
                # Add the assistant's response to messages
                messages.append(response_message)
                
                # Execute each tool call
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    print(f"Calling tool: {tool_name}, arguments: {tool_args}")
                    
                    # Call the MCP tool
                    result = await session.call_tool(tool_name, arguments=tool_args)
                    tool_result = result.content[0].text
                    print(f"Tool result: {tool_result}\n")
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })
                
                # Call LLM again with tool results to generate final assessment
                print("Calling LLM again with tool results to generate risk assessment...")
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

if __name__ == "__main__":
    asyncio.run(main())       

