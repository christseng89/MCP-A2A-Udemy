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
    async with httpx.AsyncClient(timeout=10.0) as http:
        response = await http.post(token_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["access_token"]


async def main():
    try:
        token = await get_auth0_token()
        # token = "12345678901234567890"
        print("Got Auth0 token:", token[:50] + "...")
    except httpx.RequestError as exc:
        print("Network error while fetching token:", exc)
        return
    except httpx.HTTPStatusError as exc:
        print(f"Auth0 HTTP error {exc.response.status_code}:", exc.response.text)
        return
    except Exception as exc:
        print("Unexpected error during token fetch:", exc)
        return

    try:
        # Initialize the client with the token
        client = Client(
            StreamableHttpTransport(
                url=API_AUDIENCE,
                headers={"Authorization": f"Bearer {token}"}
            )
        )
    except Exception as exc:
        print("Error initializing MCP client:", exc)
        return

    try:
        async with client:
            try:
                result = await client.call_tool("add", {"a": 5, "b": 7})
                print("5 + 7 =", result.content[0].text)
            except Exception as exc:
                print("Error calling tool 'add':", exc)

            try:
                # Not allowed without the required scope
                result = await client.call_tool("multiply", {"a": 3, "b": 4})
                print("3 * 4 =", result.content[0].text)
            except Exception as exc:
                print("Error calling tool 'multiply':", exc)
    except Exception as exc:
        print("Unexpected error with MCP client context:", exc)


if __name__ == "__main__":
    asyncio.run(main())
