# Research dossier: Model Context Protocol and the MinIO MCP server

Facts reconstructed from the published post; the repository facts were checked against the live README.

## Protocol
- MCP is an open standard connecting AI models to external data sources and tools through a unified interface; analogy: USB-C for AI applications. Source: https://spec.modelcontextprotocol.io/
- Architecture: host (user-facing AI app such as Claude Desktop or Cursor), client (inside the host, one isolated connection per server) and server (exposes capabilities). Source: https://docs.claude.com/en/docs/mcp
- Messages travel over JSON-RPC. Source: https://spec.modelcontextprotocol.io/
- Three primitives: resources (read-only data), tools (actions), prompts (reusable templates or workflows). Source: https://spec.modelcontextprotocol.io/
- Diagram credit: MCP lesson of the Full Stack AI Engineering course from Towards AI Academy. Source: https://academy.towardsai.net/courses/agent-engineering
- Ecosystem pointers: official GitHub organisation (SDKs, examples) and the MCP.so directory of servers and clients. Source: https://github.com/modelcontextprotocol and https://mcp.so/

## MinIO MCP server
- Built with colleague Rafa Ginard; repository public. Source: https://github.com/Rafitis/minio-mcp-server
- Seven tools: `list_buckets`, `get_bucket_info`, `create_bucket`, `delete_bucket`, `list_objects`, `get_object_info`, `delete_object`. Source: https://github.com/Rafitis/minio-mcp-server
- Built on FastMCP with async architecture, input validation with HTTP-style error codes, and separate BucketTools and ObjectTools classes. Source: https://github.com/Rafitis/minio-mcp-server
- Setup: clone, `uv sync`, `uv pip install -e .`; run `uv run python src/minio_mcp/server.py`; test with MCP Inspector. Source: https://github.com/Rafitis/minio-mcp-server
- Claude Desktop integration is a JSON config entry; after restart, natural-language requests map to tool calls. Source: https://docs.claude.com/en/docs/mcp
- Local LLM support lives on the `feature/llm-rest-api-integration` branch; tool-calling capable local models named: Mistral, Llama 3.2, Qwen; enterprise endpoints use an OpenAI-compatible API. Source: https://github.com/Rafitis/minio-mcp-server
