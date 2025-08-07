import os
import sys

from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider
from dotenv import load_dotenv

load_dotenv()


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


def _validate_auth0_domain(domain: str) -> str:
    """
    Validate Auth0 domain format.
    
    Args:
        domain: The Auth0 domain to validate
        
    Returns:
        The validated domain
        
    Raises:
        ValueError: If domain format is invalid
    """
    if not domain.startswith("https://"):
        raise ValueError("AUTH0_DOMAIN must start with https://")
    if not domain.endswith(".auth0.com") and not domain.endswith(".eu.auth0.com"):
        raise ValueError("AUTH0_DOMAIN must be a valid Auth0 domain")
    return domain


try:
    AUTH0_DOMAIN = _validate_auth0_domain(_get_required_env_var("AUTH0_DOMAIN"))
    API_AUDIENCE = os.environ.get("API_AUDIENCE", "http://localhost:8000/mcp")
    REQUIRED_SCOPES = ["read:add"]
except ValueError as e:
    print(f"Configuration error: {e}", file=sys.stderr)
    sys.exit(1)

auth = BearerAuthProvider(
    jwks_uri=f"{AUTH0_DOMAIN.rstrip('/')}/.well-known/jwks.json",
    issuer=AUTH0_DOMAIN.rstrip("/") + "/",
    audience=API_AUDIENCE,
    required_scopes=REQUIRED_SCOPES,
)

mcp = FastMCP(
    name="SecureAddServer",
    stateless_http=True,
    auth=auth,
)


@mcp.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    """
    Add two integers together.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Sum of a and b
    """
    return a + b


@mcp.tool(description="Multiply two integers")
def multiply(a: int, b: int) -> int:
    """
    Multiply two integers together.
    
    Args:
        a: First integer
        b: Second integer
        
    Returns:
        Product of a and b
    """
    return a * b


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
