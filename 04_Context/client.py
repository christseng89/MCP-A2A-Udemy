import asyncio

import mcp.types as types
from fastmcp import Client
from fastmcp.client.logging import LogMessage
from fastmcp.client.transports import StreamableHttpTransport
import json

async def message_handler(msg):
    if not isinstance(msg, types.ServerNotification):
        return

    root = msg.root
    if isinstance(root, types.ProgressNotification):
        p = root.params
        # server.py => await ctx.report_progress(progress=i, total=total)
        print(f"\n🚀 [Progress] {p.progress}/{p.total or '?'}")


async def log_handler(params: LogMessage):
    level = params.level.upper()
    print(f"📝 [Log | {level}] {params.data}")


async def main():
    transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcp/")
    client = Client(transport, message_handler=message_handler, log_handler=log_handler)

    # 📌📌 Async with client approach is cleaner, safer, and aligns with Python best practices for asynchronous resource management.
    async with client:
        tools = await client.list_tools()
        tools_names = [t.name for t in tools]
        print(f"🔧 Available Tools: {tools_names}")
        print(f"⚙️  Executing Tool: '{tools_names[0]}'…\n")

        items = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
        result = await client.call_tool(tools_names[0], {"items": items})

        processed = [c.text for c in result.content]
        converted = json.loads(processed[0])
        print("📌 Result:", converted)


if __name__ == "__main__":
    asyncio.run(main())
