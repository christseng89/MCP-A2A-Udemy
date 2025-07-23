import asyncio
import sys

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

from dotenv import load_dotenv
import os


dotenv = load_dotenv()
transport = os.getenv("MCP_TRANSPORT", "stdio")

stdio_server_params = StdioServerParameters(
    command=sys.executable,
    args=["server.py"],
    env=None,
)

SSE_SERVER_URL = "http://127.0.0.1:8000/sse"
HTTP_SERVER_URL = "http://127.0.0.1:8000/mcp/"

async def main() -> None:
    print(f"⚙️ Using '{transport.upper()}' transport\n")

    match transport.lower():    
        case "stdio":
            async with stdio_client(stdio_server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        res = await session.call_tool("add", {"a": 7, "b": 5})
                        print("7 + 5 =", res.content[0].text)            
        case "sse":
            async with sse_client(SSE_SERVER_URL) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    res = await session.call_tool("add", {"a": 7, "b": 5})
                    print("7 + 5 =", res.content[0].text)


        case "http":
            async with streamablehttp_client(HTTP_SERVER_URL) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()            # JSON-RPC „initialize“
                    res = await session.call_tool("add", {"a": 7, "b": 5})
                    print("7 + 5 =", res.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
