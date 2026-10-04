# Article Guideline

- **Working title:** Plain-language guide to MCP with an object-storage server as the worked example.
- **Bucket:** explainers
- **Audience:** data and AI practitioners building LLM applications and data engineers
- **Angle:** Motivate the integration problem, explain the protocol's parts, then make it concrete with a real server and local-model usage.

## Section intents

1. Describe the frustration of making models work with real data and why custom connectors do not scale.
2. Define the protocol with a simple analogy and explain what standardisation buys.
3. Explain the host, client and server roles and the three kinds of capability a server can expose.
4. List sensible use cases for live data access.
5. Present the example server built with a colleague: its tools, design choices, setup and desktop client configuration.
6. Cover local and enterprise model usage with prompting tips, point to resources and summarise benefits per audience.

## Sources

- https://github.com/Rafitis/minio-mcp-server
- https://spec.modelcontextprotocol.io/
- https://docs.claude.com/en/docs/mcp
- https://github.com/modelcontextprotocol
- https://mcp.so/
