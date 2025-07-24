from fastmcp import FastMCP

mcp = FastMCP("Agent Workflow Server", stateless_http=True)

# ➕ Tool: for agent actions
@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

# 📄 Resource: static data controlled by the application
@mcp.resource(uri="resource://user_profile", name="user_profile", description="User info")
def user_profile_resource() -> dict:
    return {"name": "Alice", "role": "Engineer", "tokens": 12345}

# 🧭 Prompt: template-driven guidance
@mcp.prompt(name="greeting_prompt", description="Personalized greeting")
def greeting_prompt(name: str, tokens: str) -> str:
    return f"System: Hello, {name}! You are an engineer with a token balance of {tokens}."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
