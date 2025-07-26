from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_context

mcp = FastMCP(name="WeatherServer", stateless_http=True)


@mcp.tool(
    name="get_weather",
    description="Returns a weather description for a given city",
)
def get_weather(city: str) -> str:
    """
    Args:
        city (str): Name of the city
    Returns:
        str: Description of the current weather (mock data)
    """
    return "Sunny, 22°C"


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


@mcp.tool()
def divide(a: int, b: int) -> int:
    """Divide two numbers"""
    if b == 0:
        b = 1  # Avoid division by zero
    return a / b

# Resources
@mcp.resource("resource://user-data")
async def get_user_data(ctx: Context) -> dict:
    """Fetch personalized user data based on the request context."""
    # Context is available as the ctx parameter
    return {"user_id": "example"}

# Resource Template
@mcp.resource("resource://users/{user_id}/profile")
async def get_user_profile(user_id: str, ctx: Context) -> dict:
    """Fetch user profile with context-aware logging."""
    # Context is available as the ctx parameter
    return {"id": user_id}

# Prompt
@mcp.prompt
async def data_analysis_request(dataset: str, ctx: Context) -> str:
    """Generate a request to analyze data with contextual information."""
    # Context is available as the ctx parameter
    return f"Please analyze the following dataset: {dataset}"

# Utility function that needs context but doesn't receive it as a parameter
async def process_data(data: list[float]) -> dict:
    # Get the active context - only works when called within a request
    ctx = get_context()    
    await ctx.info(f"Processing {len(data)} data points")
    
# Utility to load dataset (placeholder implementation)
def load_data(dataset_name: str) -> list[float]:
    """
    Mock dataset loader — replace with real logic as needed.
    e.g. read from CSV, database, or external API.
    """
    # Example static dataset
    return [1.2, 3.4, 5.6, 7.8]  # Replace with actual data loading procedure
    
@mcp.tool
async def analyze_dataset(dataset_name: str) -> dict:
    # Call utility function that uses context internally
    data = load_data(dataset_name)
    await process_data(data)
    return {
        "dataset": dataset_name,
        "data_points": len(data),
        "data": data
    }
    

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=3000)
