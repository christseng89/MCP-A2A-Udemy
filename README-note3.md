# MCP - Practical Guide 3

## Integrate MCP with GenAI Framework

https://github.com/langchain-ai/langchain-mcp-adapters
**https://gofastmcp.com/getting-started/welcome**

```cmd
cd 08_LangGraph_MCP
uv run server.py
```
---

```cmd
cd 08_LangGraph_MCP
npx @modelcontextprotocol/inspector
    Transport Type = Streamable-HTTP
    URL = http://127.0.0.1:8000/mcp
```

```cmd
cd 08_LangGraph_MCP
uv run client.py
```

## **MCP Authorization**

* **Purpose**: In production use of MCP (Model Context Protocol), protecting against unauthorized access is *essential*.
* **Mechanism**: MCP supports authorization using **OAuth 2.1**.
* **Scope**: Authorization is performed for **MCP clients**—that is, the agent or application using the tools— *not individual end users*.

---

### 🧭 What This Means

According to the official MCP specification:

1. **OAuth 2.1 is mandatory** for any MCP server implementing authorization. Servers *must* implement secure flows (e.g. Authorization Code with PKCE) for both public and confidential clients.
   ([Ory Corp][1], [Model Context Protocol][2], [Stytch][3], [WorkOS][4])

2. MCP servers **should support dynamic client registration** (RFC 7591) to automatically onboard new clients.
   ([Model Context Protocol][2])

3. MCP servers **should publish metadata** via OAuth Authorization Server Metadata (RFC 8414) or Protected Resource Metadata (RFC 9728). Clients *must* use discovery to locate the server’s endpoints.
   ([Model Context Protocol][5])

---

### ✅ Authorization Flow (Typical Sequence)

* An MCP client attempts to call a protected tool on the MCP server.
* The server responds with a **401 Unauthorized** and includes metadata pointing to its authorization endpoints.
* The client initiates the **OAuth 2.1 Authorization Code flow**, using **PKCE** for security.
* The client may perform **dynamic client registration** (POST to `/register`) if not pre-registered.
* After user consent, the client receives an authorization code and exchanges it for an access token (`/token` endpoint).
* The client uses the acquired **Bearer token** to access MCP tools.
* The server validates the token (signature, audience, expiration, scopes) before responding.
  ([Model Context Protocol][5], [Stytch][3], [Auth0][6])

---

### 🧩 Authorization vs. Authentication

* MCP servers act as **OAuth resource servers**, validating access tokens—but they can also optionally act as **authorization servers**, issuing tokens and managing registration if no third-party identity provider is used.

* Many implementations delegate token issuance and consent flows to dedicated providers like **Auth0, Stytch**, or custom identity services.
  ([developers.cloudflare.com][7], [Stytch][8])

* Alternatively, a lighter-weight approach is to use **Bearer Token authentication**, validating pre-issued JWTs without a full OAuth flow, useful in machine-to-machine communication. Note: this deviates from the spec.
  ([FastMCP][9])

---

### 🧠 Key Takeaways

* Authorization is at the **client** level—not individual users.
* OAuth 2.1 with **PKCE**, metadata discovery, and dynamic registration are core spec requirements.
* Servers must either implement full OAuth endpoints themselves or delegate to an external provider.
* For simple, internal use-cases, **Bearer tokens** can serve as a minimal workaround—but lacks compliance with full OAuth 2.1 requirements.

---


### ✅ MCP Authorization Flow (Horizontal Layout)

```plaintext
Client 🤖
   |
   | 1. Request Token
   |-----------------------------------> 
   |                                   |
   |         Authorization Server      |
   |                                   |
   | <-----------------------------------
   | 2. Returns JWT
   |
   | 3. Sends HTTP request with JWT
   | (Authorization: Bearer <token>)
   |----------------------------------->
   |                                   |
   |             MCP Server            |
   |                                   |
   | <-----------------------------------
   | 4. (Internally) Validates JWT with
   |    Authorization Server or local logic 
   |    (including audience, expiration, and scope)
   | 5. Server responds to client
   |

```

---

### 🔐 Summary

* **Client** requests an access token from the **Authorization Server**.
* The **Authorization Server** returns a **JWT** (access token).
* The **Client** sends a request to the **MCP Server**, including the JWT in the HTTP `Authorization` header.
* The **MCP Server** validates the JWT (including `scope`, signature, and expiration).
* If valid, the **MCP Server** processes the request and returns the response to the **Client**.

---

### 🔁 Responsibility Separation

* **Authorization Server** (e.g., Auth0):
  Handles identity, access token issuance, and scope management.

* **MCP Server**:
  Executes tool calls, manages resources, and enforces access control.

---

### Auth0 Setting Up

```cmd
uv run fastmcp version
  FastMCP version:             2.10.6***>=2.10.6
  MCP version:                 1.12.1
  ...
```

**Login Auth0** > Applications > APIs > Create API

**Name** `mcp-PracticalGuide-Staging`
**Identifier** `http://localhost:8000/mcp`

-> Create > Permissions 

**Permission**	read:add
**Description**	Perform add function in MCP server

-> Add > Machine to Machine Applications

**Permission**	read:add

-> Update > Continue > Test

```bash
curl --request POST \
  --url https://....auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{
    "client_id":"rzvKJpo34pJk...",
    "client_secret":"42sa_QSKz...",
    "audience":"http://localhost:8000/mcp",
    "grant_type":"client_credentials"
  }'
```

```.env
AUTH0_DOMAIN=....auth0.com
AUTH0_AUDIENCE=http://localhost:8000/mcp
AUTH0_CLIENT_ID=rzvKJpo34pJk...
AUTH0_CLIENT_SECRET=42sa_QSKz...
---

```cmd
cd 09_Authorization
uv run server.py
```

```cmd
cd 09_Authorization
npx @modelcontextprotocol/inspector
  Transport Type = Streamable-HTTP
  URL = http://localhost:8000/mcp
```
```cmd
cd 09_Authorization
uv run client.py
```

## **FastAPI Integration**

**MCP + FastAPI = ❤️**

* FastAPI is the modern standard for Python **web backends**—it's fast, async‑friendly, and developer‑friendly.
* FastMCP integrates easily with FastAPI since both run on Uvicorn.

**Two ways to integrate:**

1. **FastAPI → MCP**

   * Generate an MCP server *from* your FastAPI app using **`FastMCP.from_fastapi(...)`**
   * Exposes your existing routes as MCP tools automatically.
     使用 FastMCP.from_fastapi(app) 将**已有的 FastAPI** 应用转换为 ***MCP 服务器***。MCP 服务器，FastMCP 会自动将端点封装成 **MCP 工具或资源**。

2. **MCP → FastAPI (via mount)**

   * Build a standalone `FastMCP` server and mount it into a FastAPI app using **`mcp.http_app(...)`** or **`.streamable_http_app(...)`**
   * Allows you to use FastAPI for everything else (e.g. health checks, REST endpoints) and delegate AI tool functionality to the MCP server.
   手动构建 **FastMCP 服务器**，然后使用 **`mcp.http_app(...)`** or **`.streamable_http_app(...)`** 挂载进 **FastAPI 应用**，这样可以在一个服务中同时提供传统 API 和 MCP 功能。

**Recommended pattern**

* Use **MCP for tools, resources, and prompts** (the AI‑exposed components)
* Use **FastAPI for everything else**, such as health checks, human‑facing APIs, web UIs, etc.

---

### ✅ Why This Combo Works

By combining these, you get the best of both worlds:

* **FastAPI** gives you the mature HTTP framework, data validation, dependency injection, and standard REST API support.
* **FastMCP** provides AI‑optimized tooling—tools and resources that agents (like LLMs) can call via the Model Context Protocol.
* Mounting an MCP server inside FastAPI (or generating one from FastAPI) allows you to maintain a unified, consistent application stack served by Uvicorn, without duplication.

---

### Real‑World Integration Examples

* **FastAPI → MCP**: Developers can bootstrap an MCP layer on top of existing REST endpoints. For example, turning your `/users/{id}` route into a tool that AI agents can call with proper input validation and documentation.
* **MCP → FastAPI mount**: You might build a specialized MCP toolset (e.g. analytics or AI actions) and mount it inside a FastAPI server under `/mcp`. This isolates AI‑focused logic while your main endpoints and health metrics live natively in FastAPI.

[1]: https://gofastmcp.com/integrations/fastapi?utm_source=chatgpt.com "FastAPI FastMCP"
[2]: https://medium.com/%40madhuripenikalapati/building-a-leave-management-system-with-fastapi-and-fastmcp-391539059793?utm_source=chatgpt.com "Building a Leave Management System with FastAPI and FastMCP"

---
#### **FastAPI → MCP**

```python fastapi_mcp_server.py
...
mcp = FastMCP.from_fastapi(app=app, name="ProductMCP")
...
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=3000)


```

```cmd
cd 10_Fastapi_Integration
uv run fastapi_mcp_server.py

```

```cmd
cd 10_Fastapi_Integration
uv run fastapi_mcp_client.py

uv run fromapp_client.py # Original FastAPI MCP Client
```


#### **MCP → FastAPI (via mount)**

```python app.py
from server import mcp
...
mcp_app = mcp.http_app(path="/mcp")
app = FastAPI(lifespan=mcp_app.router.lifespan_context)
app.mount("/mcpserver", mcp_app)

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
```

```python client.py
transport = StreamableHttpTransport(url="http://127.0.0.1:8000/mcpserver/mcp")
...
```

```cmd
cd 10_Fastapi_Integration
uv run app.py
```

```cmd
cd 10_Fastapi_Integration
uv run client.py
```

## **Composition**
**Composition**: Combination of multiple MCP Servers (codelevel) into a single MCP Server
Allows **modular** structure for development (e.g. different dev teams)

```python
add_server = FastMCP(name="AddServer")

@add_server.tool(description="Add two integers")
def add(a: int, b: int) -> int:
    print(f"Executing add tool with a={a}, b={b}")
    return a + b
```

```python
subtract_server = FastMCP(name="SubtractServer")

@subtract_server.tool(description="Subtract two integers")
def subtract(a: int, b: int) -> int:
    print(f"Executing subtract tool with a={a}, b={b}")
    return a - b
```

```python
main_app = FastMCP(name="MainApp")

main_app.mount("add", add_server)
main_app.mount("subtract", subtract_server)
```

---

```cmd
cd 11_Composition
uv run server.py
```

```cmd
cd 11_Composition
uv run client.py
```

---

## MCP Proxy

```cmd
cd 12_Proxy_Servers
uv run backend_server_1.py
  http://127.0.0.1:9001/mcp/ 
```

```cmd
cd 12_Proxy_Servers
uv run backend_server_2.py
  http://127.0.0.1:9002/mcp/ 
```

```cmd
cd 12_Proxy_Servers
uv run configurable_proxy.py
  http://127.0.0.1:8000/mcp/ 
```

```cmd
cd 12_Proxy_Servers
uv run client.py
```

---

