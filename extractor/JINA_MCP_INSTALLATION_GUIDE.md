# Jina MCP Installation Guide (OpenAI Codex & VS Code)

This guide explains how to connect the official Jina AI remote MCP server (`https://mcp.jina.ai/sse`) to the OpenAI Codex CLI and to VS Code (via the Continue extension). Both setups allow you to call Jina tools such as `read_url`, `search_web`, `search_arxiv`, `parallel_*`, `deduplicate_strings`, and `sort_by_relevance` directly from your IDE or terminal.

## Prerequisites

1. **Node.js 18+** with `npx` available on your PATH.
2. **mcp-remote** helper (installed automatically via `npx` the first time it runs).
3. Optional but recommended: a Jina API key from [https://jina.ai](https://jina.ai). Some MCP tools work without a key, but authenticated requests gain higher rate limits and access to `search_web`, `search_arxiv`, `search_images`, and embeddings/reranker functionality.

Store the key in an environment variable so both Codex and VS Code can reuse it:

```powershell
# PowerShell profile (current session)
$env:JINA_API_KEY = "jina_your_key"

# Persisted for future sessions
[System.Environment]::SetEnvironmentVariable("JINA_API_KEY", "jina_your_key", "User")
```

On macOS/Linux:

```bash
export JINA_API_KEY="jina_your_key"
```

---

## 1. OpenAI Codex CLI

Codex reads MCP definitions from `~/.codex/config.toml`. Add the Jina server by pointing Codex to `mcp-remote`, which maintains the SSE connection on your behalf.

1. Open (or create) `~/.codex/config.toml`.
2. Append the following block:

```toml
[mcp_servers.jina-mcp-server]
command = "npx"
args = [
    "-y",
    "mcp-remote",
    "https://mcp.jina.ai/sse",
    "--header",
    "Authorization: Bearer ${JINA_API_KEY}"
]
```

Notes:
- Remove the `Authorization` header (and `--header` line) if you want to run in anonymous/low-rate mode.
- On Windows + PowerShell you can avoid escaping headaches by referencing an env var without spaces inside the argument, e.g. `Authorization:${AUTH_HEADER}` and setting `AUTH_HEADER="Bearer <key>"` in the `env` section.

3. Restart any running `codex` sessions, then verify the registration:

```bash
codex mcp list
```

You should see `jina-mcp-server` in the output. Run a quick smoke test:

```bash
codex mcp call jina-mcp-server read_url --json '{"url":"https://jina.ai"}'
```

If you receive structured markdown back, the MCP server is ready.

---

## 2. VS Code (Continue Extension)

VS Code does not speak MCP natively, so install the [Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue) extension or another MCP-aware assistant (Cursor, Claude Code, Cline all follow similar configuration patterns). The steps below assume Continue.

1. Install Continue and open its settings (`Ctrl+,` → search for “Continue: MCP Servers” or edit your global `settings.json`).
2. Add the server definition under `continue.mcpServers`:

```json
"continue.mcpServers": {
  "jina-mcp-server": {
    "command": "npx",
    "args": [
      "-y",
      "mcp-remote",
      "https://mcp.jina.ai/sse",
      "--header",
      "Authorization: Bearer ${JINA_API_KEY}"
    ]
  }
}
```

3. Reload VS Code (or run “Developer: Reload Window”) so Continue restarts its MCP processes.
4. Open the Continue side panel → “Tools” → confirm `jina-mcp-server` is listed. Click “Refresh tools” if you do not see the full set (some clients cache tool manifests).
5. Optional Windows workaround: Cursor/Claude Desktop on Windows occasionally mishandle arguments with spaces. If you hit “Server disconnected” errors, switch the `args` entry to `Authorization:${AUTH_HEADER}` and add an `env` block:

```json
"continue.mcpServers": {
  "jina-mcp-server": {
    "command": "npx",
    "args": [
      "-y",
      "mcp-remote",
      "https://mcp.jina.ai/sse",
      "--header",
      "Authorization:${AUTH_HEADER}"
    ],
    "env": {
      "AUTH_HEADER": "Bearer ${JINA_API_KEY}"
    }
  }
}
```

6. Test from Continue’s chat window:
   - Prompt: “Use `search_web` via jina-mcp-server to find current digital health grants.”
   - The tool call output should appear in the transcript; expand it to inspect the JSON payload.

### Troubleshooting

- **Missing tools**: remove and re-add the MCP entry to force a refresh.
- **Looping tool calls / context overflow**: increase the model’s context window or limit concurrent tool invocations when using “thinking” models.
- **Rate limits**: unauthenticated requests hit strict quotas—add your API key to unlock higher throughput.

With these setups in place you can switch to Jina MCP tools directly from Codex or VS Code without writing custom glue code.
