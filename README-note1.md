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
git clone https://github.com/christseng89/MCP-A2A-Udemy.git
cd MCP-A2A-Udemy

uv sync
```
