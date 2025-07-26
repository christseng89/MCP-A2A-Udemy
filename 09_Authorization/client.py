import asyncio
import os

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from dotenv import load_dotenv

load_dotenv()

AUTH0_DOMAIN = os.environ["AUTH0_DOMAIN"]
AUTH0_CLIENT_ID = os.environ["AUTH0_CLIENT_ID"]
AUTH0_CLIENT_SECRET = os.environ["AUTH0_CLIENT_SECRET"]
API_AUDIENCE = os.environ.get("API_AUDIENCE", "http://localhost:8000/mcp")


async def get_auth0_token() -> str:
    """
    Request an access token from Auth0 using the Client Credentials Grant.
    """
    token_url = f"{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": API_AUDIENCE,
    }
    async with httpx.AsyncClient() as http:
        response = await http.post(token_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["access_token"]


async def main():
    try:
        token = await get_auth0_token()
    except Exception as e:
        print("Error getting Auth0 token:", e)
        return
    print("Got Auth0 token:", token[:50] + "...")

    client = Client(
        StreamableHttpTransport(
            url=API_AUDIENCE,
            headers={"Authorization": f"Bearer {token}"}
        )
    )

    async with client:
        try:
            result = await client.call_tool("add", {"a": 5, "b": 7})
            print("5 + 7 =", result[0].text)

            # Not allowed without the required scope
            result = await client.call_tool("multiply", {"a": 3, "b": 4})
            print("3 * 4 =", result[0].text)
        except Exception as e:
            print("Error calling tool:", e)

if __name__ == "__main__":
    asyncio.run(main())
