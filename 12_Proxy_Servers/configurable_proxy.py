from fastmcp import FastMCP

config = {
    "mcpServers": {
        "add": {
            "url": "http://127.0.0.1:9001/mcp",
            "transport": "streamable-http"
        },
        "subtract": {
            "url": "http://127.0.0.1:9002/mcp",
            "transport": "streamable-http"
        }
    }
}

proxy = FastMCP.as_proxy(config, name="ModernProxyToLegacy")

if __name__ == "__main__":
    print("starting proxy on port 8000")
    proxy.run(transport="streamable-http", host="127.0.0.1", port=8000)
