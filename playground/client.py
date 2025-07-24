import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = "http://127.0.0.1:8000/mcp/"

async def run_agent():
    async with streamablehttp_client(MCP_URL) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()

            res = await session.read_resource("resource://user_profile")
            profile = json.loads(res.contents[0].text)
            name = profile["name"]
            tokens = str(profile["tokens"])  # convert to string

            prompt_msg = await session.get_prompt(
                "greeting_prompt",
                {"name": name, "tokens": tokens}
            )
            print("\n💬 Prompt:", prompt_msg.messages[0].content.text)

            # You can still call tools as needed:
            result = await session.call_tool("add", {"a": 2, "b": 3})
            print("2 + 3 =", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(run_agent())
