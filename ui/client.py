import streamlit as st
import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import mcp.types as types
import json

class LoggingCollector:
    def __init__(self):
        self.log_messages: list[LoggingMessageNotificationParams] = []

    async def __call__(self, params: LoggingMessageNotificationParams) -> None:
        self.log_messages.append(params)

logging_collector = LoggingCollector()

async def message_handler(
        message: RequestResponder[types.ServerRequest, types.ClientResult]
        | types.ServerNotification
        | Exception,
    ) -> None:
        print("Received message:", message)
        if isinstance(message, Exception):
            raise message
        else:
            if isinstance(message, types.ServerNotification):
                print("NOTIFICATION:", message)
            elif isinstance(message, RequestResponder):
                print("REQUEST_RESPONDER:", message)
            else:
                print("SERVER_REQUEST:", message)

async def get_credit_score(name: str):
    """Calls the credit_score tool on the MCP server."""
    print("Starting client...")
    # Connect to a streamable HTTP server
    async with streamablehttp_client("http://localhost:8000/mcp") as (
        read_stream,
        write_stream,
        session_callback,
    ): 
        # Create a session using the client streams
        async with ClientSession(
            read_stream, 
            write_stream,
            logging_callback=logging_collector,
            message_handler=message_handler,
        ) as session:

            # not initialized, should be None
            id = session_callback()
            print("ID: ", id)

            # Initialize the connection
            await session.initialize()

            id = session_callback()
            print("ID: ", id)

            print("Session initialized, ready to call tools.")
          
            # Call a tool
            results = []
            tool_result = await session.call_tool("credit_score", {"ssn": "123-45-6789"})
                    
            gen = None
            # If the tool_result is an async generator, print its items

            # Convert tool_result.text to an AsyncGenerator if it's awaitable or async iterable
           
            # Change 'ssn' to 'score' when Experian comes back on line
            score = json.loads(tool_result.content[0].text)['credit_score_info']['score']
            print(f"Tool result: {score}")
            # extract and print the score from the tool_result
            print(f'score = {tool_result.content[0].text}')
            print(f'tool_result type = {type(tool_result.content[0].text)}')

            # log = logging_collector.log_messages[0]
            # print("Log message:", log)
            credit_report = json.loads(tool_result.content[0].text)
            return credit_report

st.title("Experian Credit Check - an MCP Client")

name = st.text_input("Enter the SSN:", value="123-45-6789")

if st.button("Get Credit Report"):
    if name:
        with st.spinner("Calling credit_score tool..."):
            result = asyncio.run(get_credit_score(name))
            st.write("Credit Report:", result)
    else:
        st.warning("Please enter a name.")
