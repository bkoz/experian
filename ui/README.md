# Streamlit UI Client

Launch the server with http the transport.
```bash
uv run src/server.py --transport=streamable-http
```

```console
2025-11-18 07:19:13,200 INFO     server.py:81 - Obtained Experian access token.
2025-11-18 07:19:13,205 INFO     server.py:229 - Starting Experian MCP Server with streamable-http transport on 127.0.0.1:8000
INFO:     Started server process [10550]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Launch the UI client
```bash
cd ui
uv run streamlit run client.py
```

