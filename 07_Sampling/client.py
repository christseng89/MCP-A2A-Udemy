import asyncio

from dotenv import load_dotenv
from fastmcp import Client
from fastmcp.client.sampling import RequestContext, SamplingMessage, SamplingParams
from fastmcp.client.transports import StreamableHttpTransport
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()
def print_sampling_messages(messages):
    print("\n💬 Sampling Messages")
    print("=====================")

    for i, msg in enumerate(messages, 1):
        print(f"🔹 Message {i}")
        print(f"   🧑 Role: {msg.role}")

        if hasattr(msg.content, "text"):
            print("   📄 Content:")
            print(indent_text(msg.content.text))
        else:
            print(f"   ⚠️ Unsupported content type: {msg.content}")

        print()  # extra newline between messages

    print("==================\n")

def print_sampling_params(params):
    print("🧪 Sampling Params")
    print("==================")

    if getattr(params, "systemPrompt", None):
        print(f"🧠 System Prompt: {params.systemPrompt}")

    if hasattr(params, "messages") and params.messages:
        print("\n💬 Human Messages:")
        for i, msg in enumerate(params.messages, 1):
            print(f"  [{i}] Role: {msg.role}")
            if hasattr(msg.content, 'text'):
                print(f"      Content:\n{indent_text(msg.content.text)}")
            else:
                print(f"      Content: {msg.content}")

    if getattr(params, "temperature", None) is not None:
        print(f"\n🌡️ Temperature: {params.temperature}")

    if getattr(params, "maxTokens", None) is not None:
        print(f"\n🔢 Max Tokens: {params.maxTokens}")

    if getattr(params, "stopSequences", None):
        print(f"🛑 Stop Sequences: {params.stopSequences}")

    if getattr(params, "includeContext", None):
        print(f"\n📎 Include Context: {params.includeContext}")

    if getattr(params, "modelPreferences", None):
        print(f"\n⚙️ Model Preferences: {params.modelPreferences}")

    if getattr(params, "metadata", None):
        print(f"\n🗂️ Metadata: {params.metadata}")

    print("==================\n")


def indent_text(text, indent="      "):
    return "\n".join(indent + line for line in text.strip().splitlines())


async def sampling_handler(
    messages: list[SamplingMessage], params: SamplingParams, context: RequestContext
) -> str:
    # print("\n[Client] sampling_handler invoked")
    print(f"[Client] Received {len(messages)} message(s)")
    print_sampling_messages(messages)
    print_sampling_params(params)

    llm_messages = []

    # System Message
    if params.systemPrompt:
        # print("[Client] Using system_prompt:", params.systemPrompt)
        llm_messages.append(SystemMessage(content=params.systemPrompt))

    # Human Messages
    for idx, msg in enumerate(messages, start=1):
        # print(f"[Client] Message #{idx} content:", msg.content.text)
        llm_messages.append(HumanMessage(content=msg.content.text))

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=params.temperature or 0.0,
        max_tokens=params.maxTokens or 64,
    )

    result = await llm.ainvoke(input=llm_messages)
    return result.content


async def main():
    transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcp/")
    client = Client(
        transport, 
        sampling_handler=sampling_handler
        )

    # Example function code for which we want a docstring
    code_snippet = """\
def add(a: int, b: int) -> int:
    return a + b
"""

    async with client:
        print("\n🔍 Requesting docstring generation for the code snippet...")            
        result = await client.call_tool("generate_docstring", {"code": code_snippet})
        print("🧠 LLM generated docstring:\n", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
