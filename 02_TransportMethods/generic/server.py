from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

dotenv = load_dotenv()
transport = os.getenv("MCP_TRANSPORT", "stdio")

mcp = FastMCP(f"Add {transport.upper()} Server")


@mcp.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    return a + b


if __name__ == "__main__":
    if transport.lower() == "http":
        transport = "streamable-http"

    print(f"🟢 Starting {transport.upper()} server...\n") 
    mcp.run(transport=transport.lower())
