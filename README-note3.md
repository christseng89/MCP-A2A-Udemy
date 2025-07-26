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

Applications > APIs > Create API

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
