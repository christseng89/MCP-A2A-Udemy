import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

SERVER = "http://127.0.0.1:8000/mcp/"


async def fetch_recipe_and_generate_prompt(session: ClientSession, recipe: str) -> None:
    recipe_response = await session.read_resource(f"recipe://{recipe}")
    recipe_text = recipe_response.contents[0].text
    print("\nRecipe:\n", recipe_text)

    prompt_response = await session.get_prompt(
        "review_recipe",
        {"recipe": recipe_text},
    )
    print("\nPrompt messages:")
    for message in prompt_response.messages:
        print(f"[{message.role}] {message.content.text}")

async def main() -> None:
    async with streamablehttp_client(SERVER) as (read, write, _):
        async with ClientSession(read, write) as session:
            resources = await session.list_resources()
            resources_uris = [r.uri for r in resources.resources]
            print("\nResource URIs:", resources_uris)
            read_resource = await session.read_resource(resources_uris[0])
            print("Read Resource:", read_resource.contents[0].text)

            # List all available resource templates
            templates = await session.list_resource_templates()
            print("\nResource Template URIs:", [t.uriTemplate for t in templates.resourceTemplates])
            
            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])

            prompts = await session.list_prompts()
            # print("\nPrompts:", prompts.prompts)
            print("Prompts Name:", [p.name for p in prompts.prompts])

            doubled_response = await session.call_tool("double", {"n": 21})
            doubled_value = doubled_response.content[0].text
            print(f"\n21 doubled -> {doubled_value}")

            await fetch_recipe_and_generate_prompt(session, "chili_con_carne")
            await fetch_recipe_and_generate_prompt(session, "pancakes")
            await fetch_recipe_and_generate_prompt(session, "apple_pie")  # Non-existent recipe to test error handling

if __name__ == "__main__":
    asyncio.run(main())
