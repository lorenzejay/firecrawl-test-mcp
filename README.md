# crewai-firecrawl-mcp-test

A single crewAI agent that researches a topic using the [Firecrawl MCP server](https://github.com/firecrawl/firecrawl-mcp-server) over streamable HTTP.

The agent searches the live web with `firecrawl_search`, reads the most promising
pages with `firecrawl_scrape`, and returns a short sourced briefing.

## Installation

Requires Python >=3.10 <3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Configuration

Add these to `.env`:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | LLM used by the agent |
| `FIRECRAWL_API_KEY` | Firecrawl key, sent as the `x-firecrawl-api-key` header |

`FIRECRAWL_API_KEY` is optional. Without it the agent falls back to the hosted
keyless tier, which is rate limited but still allows search and scrape. Get a key
at [firecrawl.dev](https://www.firecrawl.dev/app/api-keys).

## Running

```bash
# Topic as a command line argument
uv run kickoff "recent benchmarks comparing AI coding agents"

# Or via the RESEARCH_TOPIC env var, which is what `crewai run` uses
RESEARCH_TOPIC="state of MCP adoption" crewai run
```

With no topic given, it researches the default in `DEFAULT_TOPIC`.

## How it works

Everything lives in `src/crewai_firecrawl_mcp_test/main.py`:

- `firecrawl_mcp()` builds an `MCPServerHTTP` config pointed at
  `https://mcp.firecrawl.dev/v2/mcp` with `streamable=True`. The API key goes in a
  header rather than the URL path so it stays out of the generated tool names.
  A static tool filter narrows the server's 26 tools down to
  `firecrawl_search` and `firecrawl_scrape`.
- `research()` creates one `Agent` with that MCP server attached via `mcps=[...]`
  and runs a single `Agent.kickoff()`.

Note: `mcp` is pinned to `<2` because crewAI 1.6.1's HTTP transport imports
`streamablehttp_client`, which mcp 2.x renamed.

## Support

- [crewAI documentation](https://docs.crewai.com)
- [crewAI GitHub](https://github.com/crewAIInc/crewAI)
- [Firecrawl MCP server](https://github.com/firecrawl/firecrawl-mcp-server)
