import asyncio
import os
import sys

import httpx
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from dotenv import load_dotenv

load_dotenv()


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class MCPClientError(Exception):
    """Raised when MCP client operations fail."""
    pass


def _get_required_env_var(var_name: str) -> str:
    """
    Get required environment variable with validation.
    
    Args:
        var_name: Name of the environment variable
        
    Returns:
        The environment variable value
        
    Raises:
        ValueError: If the environment variable is not set or empty
    """
    value = os.environ.get(var_name)
    if not value:
        raise ValueError(f"Required environment variable {var_name} is not set")
    return value


try:
    AUTH0_DOMAIN = _get_required_env_var("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID = _get_required_env_var("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = _get_required_env_var("AUTH0_CLIENT_SECRET")
    API_AUDIENCE = os.environ.get("API_AUDIENCE", "http://localhost:8000/mcp")
except ValueError as e:
    print(f"Configuration error: {e}", file=sys.stderr)
    sys.exit(1)


async def get_auth0_token() -> str:
    """
    Request an access token from Auth0 using the Client Credentials Grant.
    
    Returns:
        The access token string
        
    Raises:
        AuthenticationError: If token request fails
    """
    token_url = f"{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": API_AUDIENCE,
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            response = await http.post(token_url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if "access_token" not in data:
                raise AuthenticationError("No access token in response")
                
            return data["access_token"]
    except httpx.RequestError as exc:
        raise AuthenticationError(f"Network error while fetching token: {exc}")
    except httpx.HTTPStatusError as exc:
        raise AuthenticationError(f"Auth0 HTTP error {exc.response.status_code}")
    except Exception as exc:
        raise AuthenticationError(f"Unexpected error during token fetch: {exc}")


async def main():
    """
    Main function to authenticate and interact with MCP server.
    """
    try:
        token = await get_auth0_token()
        print("Got Auth0 token:", token[:50] + "...")
    except AuthenticationError as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
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
        raise MCPClientError(f"Error initializing MCP client: {exc}")

    try:
        async with client:
            # Test allowed operation
            try:
                result = await client.call_tool("add", {"a": 5, "b": 7})
                print("5 + 7 =", result.content[0].text)
            except Exception as exc:
                print(f"Error calling tool 'add': {exc}", file=sys.stderr)

            # Test operation that might not be allowed due to scope restrictions
            try:
                result = await client.call_tool("multiply", {"a": 3, "b": 4})
                print("3 * 4 =", result.content[0].text)
            except Exception as exc:
                print(f"Error calling tool 'multiply' (may be scope restricted): {exc}")
    except MCPClientError as exc:
        print(f"MCP client error: {exc}", file=sys.stderr)
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
