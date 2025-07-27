import asyncio
import json
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

SERVER = "http://127.0.0.1:3000/mcp/"

LIST_PRODUCTS = 'list_products_products_get'
CREATE_PRODUCT = 'create_product_products_post'


async def main():
    async with Client(StreamableHttpTransport(SERVER)) as client:
        resources = await client.list_resources()
        print("Available Resources")
        for res in resources:
            print(f"📌 Resource Name: {res.name}    URI: {res.uri}")

        list_uri = str(resources[0].uri)
        all_products = await client.read_resource(list_uri)
        print("\n📦 All Products via Resource(Before):", all_products[0].text
              )
        tools = await client.list_tools()
        print("\n🔧 Available Tools:", [t.name for t in tools])

        if LIST_PRODUCTS not in [t.name for t in tools]:
            print(f"❌ Tool '{LIST_PRODUCTS}' not found in available tools.")
            return
        if CREATE_PRODUCT not in [t.name for t in tools]:
            print(f"❌ Tool '{CREATE_PRODUCT}' not found in available tools.")
            return

        # 调用 list_products 接口
        tool_list = LIST_PRODUCTS
        print(f"\n🚀 Calling tool: {tool_list}")
        result = await client.call_tool(tool_list, {})
        # result 是 CallToolResult，通常包含一条 content
        resp = result.content[0].text
        print("📦 List Products Response:", resp)

        # 将 JSON 字符串解析为 Python 对象
        products = json.loads(resp)
        print("Parsed Products:", products)

        # 调用 create_product 接口
        create_tool = CREATE_PRODUCT
        payload = {"name": "Widget", "price": 19.99}
        print(f"\n🚀 Calling tool: {create_tool} with payload {payload}")
        result2 = await client.call_tool(create_tool, payload)
        resp2 = result2.content[0].text
        print("📦 Created Product Response:", resp2)
        new_product = json.loads(resp2)
        print("Parsed New Product:", new_product)

        # 再次调用 list_products，以查看更新后的列表
        print("\n🔁 Calling list again:")
        result3 = await client.call_tool(tool_list, {})
        updated = json.loads(result3.content[0].text)
        print("Updated Products:", updated)

if __name__ == "__main__":
    asyncio.run(main())
