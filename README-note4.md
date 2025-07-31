# MCP - Practical Guide 4

## **Capstone Project**

- **Full-stack**, **production**-grade **LLM Agent chatbot app** with **MCP server** and **authorization**
    This will be a high-level overview — not a line-by-line walkthrough

- **Architecture matters more than actual code**

**Tip:** Play around with the codebase and adapt it to your own use case (maybe even as a portfolio project on your dev journey)

---

### Capstone DEMO

*Enhance **furniture_client_agent.py** to work with Serper MCP Server*

```cmd
cd 13_Capstone
docker compose up --build
docker compose up -d

```

http://localhost:8080/
- Hi, how are you?
- What is the price for a chair?
- How many furniture items do you have?
- What is the weather today in Taipei?

### **Core Technologies**

- **Docker + Docker Compose**

```yaml
version: "3.8"

services:
  furniture_server: # MCP Server, Port 3000 (furniture_server.py)
    ...
  api_server: # FastAPI, Port 8000 (api_server.py)
  # Embedded with furniture_client_agent.py (client for furniture server + Agent)
    ...
  frontend: # Port 8080 (nginx + static files)
    ...

networks:
  app-network:
    ...
```

1. **Frontend:** Simple HTML, CSS and JavaScript Applications, send Chat Request to API Server

2. **API Server:** **FastAPI Service** that defines Chat Interface & holds **MCP CLIENT** in the Application State & obtains token from **Auth0** Identity Provider

3. **Furniture Server:** **MCP Server** that can be invoked to answer questions about furniture prices

---

### Flow of the Capstone Project


1. Users type **questions** in the UI
2. The LLM Agent (running in the **API server**) decides whether a tool is needed
3. The API server uses a cached token to invoke a function on the MCP server
4. The MCP server validates the token using the Auth0 client
5. The MCP server executes the tool and sends the result back to the API server
6. The LLM Agent uses the tool output to generate an answer, and the API server returns it to the frontend

---

#### Enhance furniture_server.py and furniture_client_agent.py to support Docker, Kubernetes, and local environments
```cmd
cd 13_Capstone
uv run furniture_server.py
```

```cmd
cd 13_Capstone
uv run furniture_client_agent.py
```

#### Enhance api_server.py to support Docker, Kubernetes, and local environments
```cmd
cd 13_Capstone
uv run api_server.py
```

```bash
curl --location 'http://127.0.0.1:8000/ask' \
--header 'Content-Type: application/json' \
--data '{
  "messages": [
    {
      "role": "human",
      "content": "How much is a chair?"
    }
  ]
}
'
```

#### Enhance a common function to detect the OS and environment
```cmd
cd 13_Capstone
uv run common_detect_os.py
```

