import asyncio
import re
from fastmcp.tools import Tool
from typing import Callable
from fastmcp import Context, FastMCP

mcp = FastMCP(name="Dynamic-Tool-Router Demo")


async def to_upper(text: str) -> str:
    return text.upper()

async def to_lower(text: str) -> str:
    return text.lower()

async def count_words(text: str) -> int:
    await asyncio.sleep(0)
    return len(re.findall(r"\w+", text))


TOOLS: dict[str, tuple[Callable, str, str]] = {
    "uppercase": (to_upper, "upper_tool", "Convert text to uppercase."),
    "lowercase": (to_lower, "lower_tool", "Convert text to lowercase."),
    "wordcount": (count_words, "wordcount_tool", "Count words in the text."),
}


def classify(text: str) -> str | None:
    text_lower = text.lower()

    # Wordcount first
    if "word" in text_lower or "count" in text_lower:
        return "wordcount"
    # Lowercase detection
    if text.isupper() or "lower" in text_lower:
        return "lowercase"
    # Uppercase detection
    if text.islower() or "upper" in text_lower:
        return "uppercase"
    
    # All uppercase characters and spaces
    if re.fullmatch(r"[A-ZÄÖÜÊẞ ]+", text):
        return "wordcount"

    return None


@mcp.tool(
    name="router",
    description="Classifies text, registers the appropriate tool, executes it, and returns the result.",
)
async def router(text: str, ctx: Context):
    category = classify(text) or "uppercase" 
    fn, tool_name, desc = TOOLS[category]

    # Dynamic tool registration >= 2.7.0
    new_tool = Tool.from_function(fn, name=tool_name, description=desc)
    ctx.fastmcp.add_tool(new_tool)    

    # ctx.fastmcp.add_tool(fn, name=tool_name, description=desc) # before 2.7.0

    result = await fn(text)
    await ctx.info(f"Result from {tool_name}: {result!r}")
    # await ctx.fastmcp.remove_tool(tool_name)  # remove the tool again if desired
    return result


if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)
