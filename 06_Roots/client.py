import asyncio
import os

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def find_file_with_client(client: Client, file_name: str) -> None:
    """Find file using the given MCP client."""
    result = await client.call_tool("find_file", {"filename": file_name})
    print(f"\n🔍 Search paths for '{file_name}':")

    if len(result.content) == 0 or not result:
        print("  ❌ No matches found")
    for r in result.content:
        print("  ✅ -", r.text)


async def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    demo_root = os.path.join(script_dir, "demo_root")
    project_root = os.path.join(demo_root, "project")
    print (f"Using project root: {project_root}")

    transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcp/")

    roots = [
        # f"file://{docs_root}",
        f"file://{project_root}",
    ]

    client = Client(
        transport, 
        roots=roots
        )

    file_name = "server.py"
    async with client:
        await find_file_with_client(client, "server.py")
        await find_file_with_client(client, "helper.py")


if __name__ == "__main__":
    asyncio.run(main())
