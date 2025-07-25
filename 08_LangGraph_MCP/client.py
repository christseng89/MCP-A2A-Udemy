import asyncio

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

load_dotenv()

def print_conversation(messages):
    print("\n🧾 Conversation History")
    print("=======================\n")
    
    for i, msg in enumerate(messages, 1):
        if msg.__class__.__name__ == "HumanMessage":
            print(f"🙋 Human {i}: {msg.content}")
        
        elif msg.__class__.__name__ == "AIMessage":
            if tool_calls := msg.additional_kwargs.get("tool_calls"):
                print(f"🤖 AI {i}: [Tool Call]")
                for call in tool_calls:
                    func_name = call.get("function", {}).get("name", "unknown")
                    args = call.get("function", {}).get("arguments", "{}")
                    print(f"   🔧 Tool Name: {func_name}")
                    print(f"   📦 Args: {args}")
            elif msg.content.strip():
                print(f"🤖 AI {i}: {msg.content}")
            else:
                print(f"🤖 AI {i}: (empty response)")
        
        elif msg.__class__.__name__ == "ToolMessage":
            print(f"🛠️ Tool Response {i} ({msg.name}): {msg.content}")
        
        else:
            print(f"❓ Unknown Message Type {i}: {msg}")

        print()  # newline between entries

    print("=======================\n")

async def main():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:3000/mcp/",
            }
        }
    )

    tools = await client.get_tools()
    agent = create_react_agent("gpt-4o-mini", tools)

    question = "How will the weather be in Munich today?"

    result = await agent.ainvoke({"messages": question})

    messages = result["messages"]
    print("\n✍️ Messages length:", len(messages))
    print_conversation(messages)

    math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12 / 3?"})
    messages = math_response["messages"]
    print("\n✍️ Messages length:", len(messages))
    print_conversation(messages)
        
if __name__ == "__main__":
    asyncio.run(main())
