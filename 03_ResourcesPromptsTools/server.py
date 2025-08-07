from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("Recipe-Stateless", stateless_http=True)

_FAKE_DB = {
    "chili_con_carne": "Chili con Carne\n• Beans\n• Ground meat\n• Chili\n…",
    "pancakes": "Pancakes\n• Flour\n• Milk\n• Eggs\n…",
}


@mcp.resource("recipes://list")
def list_recipes() -> str:
    """Returns a comma-separated list of all available recipes."""
    return ", ".join(sorted(_FAKE_DB))


@mcp.resource("recipe://{dish}") # Dynamic Resource Template
def get_recipe(dish: str) -> str:
    """
    Returns the recipe for the specified dish.
    
    Args:
        dish: Name of the dish to get the recipe for
        
    Returns:
        Recipe content or error message if not found
        
    Raises:
        ValueError: If dish parameter contains invalid characters
    """
    if not dish or not isinstance(dish, str):
        raise ValueError("Dish parameter must be a non-empty string")
    
    # Sanitize dish name to prevent injection
    sanitized_dish = dish.strip().lower()
    if not sanitized_dish.replace("_", "").replace(" ", "").isalnum():
        raise ValueError("Dish name contains invalid characters")
    
    return _FAKE_DB.get(sanitized_dish, f"No recipe found for {dish!r}.")


@mcp.tool(description="Doubles an integer.")
def double(n: int) -> int:
    """
    Doubles an integer value.
    
    Args:
        n: Integer to double
        
    Returns:
        n multiplied by 2
    """
    return n * 2


@mcp.tool(description="Add two integers.")
def add(a: int, b: int) -> int:
    """
    Add two integers together.
    
    Args:
        a: First integer to add
        b: Second integer to add
        
    Returns:
        Sum of a and b
    """
    return a + b

@mcp.prompt(description="Prompt to review a recipe")
def review_recipe(recipe: str) -> list[base.Message]:
    return [
        base.UserMessage("Please review this recipe:"),
        base.UserMessage(recipe),
    ]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
