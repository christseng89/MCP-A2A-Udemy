import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

import mcp.types as types
from fastmcp.client.logging import LogMessage

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
    async with Client(
        StreamableHttpTransport("http://127.0.0.1:8000/mcp/"), 
        message_handler=message_handler, 
        log_handler=log_handler
        ) as client:

        print("Tools BEFORE :", [t.name for t in await client.list_tools()], "\n")

        await client.call_tool("router", {"text": "please make this lower CASE"})
        print("Tools AFTER1  :", [t.name for t in await client.list_tools()], "\n")

        await client.call_tool("router", {"text": "please make this upper CASE"})
        print("Tools AFTER2  :", [t.name for t in await client.list_tools()], "\n")

        await client.call_tool("router", {"text": "Hello world to word count"})
        print("Tools AFTER3  :", [t.name for t in await client.list_tools()], "\n")

if __name__ == "__main__":
    asyncio.run(main())
