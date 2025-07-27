import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def main():
    transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcp/")
    client = Client(transport=transport)

    async with client:
        tools = await client.list_tools()
        print("=== Available Tools ===")
        for tool in tools:
            print(f"Tool Name: {tool.name}")
        print()

        result_add = await client.call_tool(tools[0].name, {"a": 5, "b": 7})
        print("5 + 7 =", result_add.content[0].text)

        result_subtract = await client.call_tool(tools[1].name, {"a": 10, "b": 3})
        print("10 - 3 =", result_subtract.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
