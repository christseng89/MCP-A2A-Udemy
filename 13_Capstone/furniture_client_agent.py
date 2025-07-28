# Uses LangGraph + LangChain to invoke the appropriate tools

import os
import traceback
from datetime import datetime, timedelta, timezone

import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import AIMessage, BaseMessage

import asyncio
from langchain_core.messages import HumanMessage

from common_detect_os import detect_runtime_env


load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"].rstrip("/")
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
API_AUDIENCE = os.environ["API_AUDIENCE"]

TOKEN_URL = f"{AUTH0_DOMAIN}/oauth/token"


class FurnitureAgent:
    def __init__(self) -> None:
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.client: MultiServerMCPClient | None = None
        self.agent = None
        self.token = None
        self.expires = datetime.min
        self.is_initialized = False

    async def _fresh_token(self) -> str:
        now = datetime.now(timezone.utc)
        if self.token and now + timedelta(seconds=60) < self.expires:
            return self.token

        payload = {
            "grant_type": "client_credentials",
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "audience": API_AUDIENCE,
            "scope": "read:add",
        }

        async with httpx.AsyncClient() as http:
            r = await http.post(TOKEN_URL, json=payload, timeout=10)
            r.raise_for_status()
            data = r.json()

        self.token = data["access_token"]
        self.expires = now + timedelta(seconds=data.get("expires_in", 3600))
        return self.token

    async def initialize(self) -> None:
        try:
            token = await self._fresh_token()
            print(f"Using token: {token[:10]}... (expires at {self.expires})")
            env = detect_runtime_env()
            if env in ["docker", "k8s"]:
                mcp_url = "http://furniture_server:3000/mcp"
            else:
                mcp_url = "http://127.0.0.1:3000/mcp"

            self.client = MultiServerMCPClient(
                {
                    "furn": {
                        "transport": "streamable_http",
                        "url": mcp_url,
                        "headers": {"Authorization": f"Bearer {token}"},
                    }
                }
            )

            print(f"Initialized MCP client with URL: {mcp_url}")

            self.client = MultiServerMCPClient(
                {
                    "furn": {
                        "transport": "streamable_http",
                        "url": mcp_url,
                        "headers": {"Authorization": f"Bearer {token}"},
                    }
                }
            )
            tools = await self.client.get_tools()
            self.agent = create_react_agent(self.llm, tools)
            self.is_initialized = True
        except Exception:
            traceback.print_exc()
            raise

    async def ask(self, messages: list[BaseMessage]) -> str:
        try:
            if not self.is_initialized:
                await self.initialize()

            token = await self._fresh_token()
            self.client.connections["furn"]["headers"]["Authorization"] = (
                f"Bearer {token}"
            )

            result = await self.agent.ainvoke({"messages": messages})
            for msg in reversed(result["messages"]):
                if isinstance(msg, AIMessage):
                    return msg.content
            return "No valid AI response."
        except Exception as e:
            traceback.print_exc()
            return f"Error: {e}"

    async def close(self):
        self.client = None
        self.agent = None
        self.is_initialized = False


async def main():
    agent = FurnitureAgent()

    # Optional: initialize explicitly
    # await agent.initialize()

    # Define a test message1
    messages = [HumanMessage(
        content="What furniture options do you recommend for a small living room?")]
    response = await agent.ask(messages)
    print("Agent response:", response)

   # Define a test message2
    messages = [HumanMessage(content="What is the price for table?")]
    response = await agent.ask(messages)
    print("Agent response:", response)

    # Clean up
    await agent.close()

if __name__ == "__main__":
    asyncio.run(main())
