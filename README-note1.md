# MCP - Practical Guide

## Course Overview

### Course Overview #1

**1. First MCP Server**
→ Basics, "Hello World" Server

**2. Transport Methods**
→ SSE vs. stdio. vs streamable-http

**3. Resources, Prompts & Tools**
→ Core MCP Concepts

**4. Context** → **Powerful** FastMCP Object
**5. Discovery**
**6. Roots**
→ Remaining three, advanced concepts

**7. Sampling**

### Course Overview #2

**8. LangGraph + MCP**
→ LLM Integration

**9. Authorization**
→ Secure your MCP Server

### Course Overview #3

**10. FastAPI Integration**
**11. Composition** 
**12. Proxy Servers**
→ MCP Architecture with FastMCP

---

### Course Overview #4

**13. Capstone**
→ Production grade multi-services system (Docker)

---

## **Why MCP is a Gamechanger**

**Developed by Anthropic**
**Utilizes JSON-RPC**
A **standard** approach for LLMs to use **tools** (and **more**!)

😊 Only a **single** connector (MCP servers) is required
😊 One, standardized interface
😊 Scalable, consistent, and clean

---

### Example - Stripe MCP Server instead of APIs calls

😊 ⟷ MCP server (Stripe API)

**Method Call:** `stripe.create_payment()`
**The protocol is open source — built with a strong community mindset.**

---

## **Introduction to JSON-RPC**

**JSON-RPC**
Lightweight protocol that combines JSON & RPC

> "Use JSON to call remote functions as if they were **local**."

```json
{
  "method": "calculate_tax",
  "params": {
    "amount": number
  },
  "returns": number
}
```

---

### **JSON-RPC vs REST**

**JSON-RPC**
"I want to run that function."
*action oriented*

**REST**
"I want to access that resource."
*resource oriented*

---

### **JSON-RPC** Execution Example

#### ✅ *Schema Definition / Conceptual Structure* - **general JSON-RPC method format**

```json
{
  "method": "calculate_tax",
  "params": {
    "amount": number
  },
  "returns": number
}
```

* It’s **not executable code**.
* Describes what the method expects (`params`) and what it returns.
* Useful for documentation or interface design.

---

### **JSON-RPC Protocol Example**

```python
payload = {
  "jsonrpc": "2.0",
  "method": "calculate_tax",
  "params": {
    "amount": 119.0
  },
  "id": 1
}

requests.post("http://localhost:8000/jsonrpc", json=payload)
```

#### **Explanation:**

* **jsonrpc**: Specifies the protocol version (e.g., `"2.0"`).
* **method**: The name of the remote function to invoke (e.g., `"calculate_tax"`).
* **params** *(optional)*: Arguments for the method. Can be passed as:

  * An **array** → e.g., `["add", [3, 2]]`
  * Or as **key-value pairs** → e.g., `{"amount": 119.0}`
* **id** *(optional)*: A unique identifier for the request, used to correlate the response with the request.  If no id is provided, the **request** is treated as a **notification** — fire-and-forget (i.e. **no response** expected).

📡 The request is sent to the server *Endpoint* **/jsonrpc** using an HTTP POST method.

---

### **Why use JSON-RPC?**

1. **VERY EASY** to use
2. **Lightweight** data format (JSON)
3. Clearly **defined method(names)**
4. **Transport-agnostic** – works over HTTP, gRPC, WebSockets, etc.

---

## Setup environment

```cmd
git clone https://github.com/christseng89/MCP-A2A-Udemy.git mcp-PracticalGuide
cd mcp-PracticalGuide

uv sync
.venv\Scripts\activate
uv pip list

```

## **Tool / Function Calling Recap**

### **What is Tool Calling and why does it matter?**

Tool calling allows an LLM to interact with the outside world — for example, querying a database or calling an API.
Almost ALL modern LLMs support Tool Calling.

---

### **Tool Calling workflow**

1. Tool Definition
2. Tool Binding
3. Tool Calling/Execution
4. The LLM uses the tool result to generate a final response

---

```python# Example of Tool Definition
ToolCalling.ipynb
```

## MCP - First Server/Client Example

```cmd
cd 01_FirstMCPServer
uv run server.py

npx @modelcontextprotocol/inspector
```

```bash by using 'jsonrpc'
cd 01_FirstMCPServer
./script.sh
  SID=bbd0b7da20fc4d13b7bda79ec91d93fc
  Result: 2 + 3 = 5

uv run client.py
  Before initialize: None
  Session ID after initialize: 0f149990984b458a8d94603fbe26420d
  Server result: meta=None content=[TextContent(type='text', text='39', annotations=None)] isError=False
  Result:  39
```

## **MCP Transport Methods**

`stdio` vs `SSE` vs `streamable-http`

### ***Stdio***

* Communicates over **standard input/output**
* Runs **locally** on a **single machine only**
* ✅ Perfect for **development and testing**
* ⚠️ ***Not recommended*** for **production environments**

### **SSE (Server-Sent Events)**

* Establishes a long-lived connection between server and client
* Server can push live updates to the client (`EventStream`)
* Client communicates via `POST` request
* Was the default until **May 2025**, now **☠ DEPRECATED**

---

#### ✅ **Pros:**

* Easy to set up
* Supports advanced use cases (e.g. sampling)

#### ❌ **Cons:**

* Not suitable for serverless environments
* Hard to keep connections alive through proxies and networks
* Difficult to scale horizontally (e.g. in Kubernetes clusters)

---

### ***Streamable-http***

* ⚙️ Enables **fully stateless** MCP servers
* ☁️ Ideal for **serverless environments** and **horizontally scalable** services
* 🔁 **Flexible**: Can switch to **stateful mode** when needed

---

🛑 **SSE is deprecated** — use **STREAMABLE-HTTP** instead!

```python
@mcp.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    return a + b
```

✅ **No need for a session :-)**

---

### Stdio 

- .env => MCP_TRANSPORT=stdio

```cmd
cd 02_TransportMethods\generic
uv run server.py
```

```cmd
cd 02_TransportMethods\generic
npx @modelcontextprotocol/inspector
  Transport Type = SSE
  COMMAND = uv run server.py
```

```cmd
cd 02_TransportMethods\generic
uv run client.py
  ➕ 7 + 5 = 12 by using STDIO transport
```

### Sse

- .env => MCP_TRANSPORT=SSE

```cmd
cd 02_TransportMethods\generic
uv run server.py
```

```cmd
cd 02_TransportMethods\generic
npx @modelcontextprotocol/inspector
  Transport Type = SSE
  URL = http://127.0.0.1:8000/sse
```

```cmd
cd 02_TransportMethods\generic
uv run client.py
  ➕ 7 + 5 = 12 by using SSE transport
```

### Streamable-http
- .env => MCP_TRANSPORT=http

```cmd
cd 02_TransportMethods\generic
uv run server.py
```

```cmd
cd 02_TransportMethods\generic
npx @modelcontextprotocol/inspector
  Transport Type = Streamable-HTTP
  URL = http://127.0.0.1:8000/mcp
```

```cmd
cd 02_TransportMethods\generic
uv run client.py
  ➕ 7 + 5 = 12 by using HTTP transport
```

```bash
cd 02_TransportMethods/generic
./stateless_http_script.sh

```

**NOTE**: 

- The `stateless_http_script.sh` is a script that demonstrates how to use the **Streamable-HTTP** transport in a stateless manner (i.e. **stateless_http=True**), which is particularly useful for **serverless** environments.

---

## **MCP Capabilities**

### **Tools** (95% of use cases)

* Usage controlled by the **LLM**
* The LLM **decides** when a tool is needed to answer a question
* Use case: Dynamically integrating data that is not part of the model's training

---

### **Resources**

* Usage controlled by the **application** (e.g., accessing a profile after a user click)
* The LLM does not dynamically reach out to use a resource

---

### **Prompts** (User-Driven Interactions)

* Usage controlled by the **user**
* Parameterized templates optimized for LLM input (e.g., dynamic `SystemMessage`)
* Clients collect user input and inject variables into **templates**

```

---

```cmd
cd 03_ResourcesPromptsTools
uv run server.py
```

```cmd
cd 03_ResourcesPromptsTools
npx @modelcontextprotocol/inspector
  Transport Type = Streamable-HTTP
  URL = http://127.0.0.1:8000/mcp

```

```cmd
cd 03_ResourcesPromptsTools
uv run client.py
  ➕ 7 + 5 = 12 by using HTTP transport
```

---
