# crewai-firecrawl-mcp-test

A crewAI Flow that researches a topic using the [Firecrawl MCP server](https://github.com/firecrawl/firecrawl-mcp-server) over streamable HTTP.

The first step searches the live web with `firecrawl_search` and reads the most
promising pages with `firecrawl_scrape`; the second turns those notes into a
short sourced briefing.

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
- `ResearchFlow` is a `Flow[ResearchState]` with two steps. `gather_sources()` is
  the `@start()` step: it creates an `Agent` with that MCP server attached via
  `mcps=[...]` and stores the raw notes in `state.findings`. `write_briefing()`
  `@listen`s for it and hands those notes to a second, tool-less agent, storing
  the result in `state.briefing`.
- Flow inputs populate the state, so `ResearchFlow().kickoff(inputs={"topic": ...})`
  is what sets `state.topic`.

Run `uv run plot` to render the flow graph as an HTML file.

Note: `mcp` is pinned to `<2` because crewAI 1.6.1's HTTP transport imports
`streamablehttp_client`, which mcp 2.x renamed.

## Support

- [crewAI documentation](https://docs.crewai.com)
- [crewAI GitHub](https://github.com/crewAIInc/crewAI)
- [Firecrawl MCP server](https://github.com/firecrawl/firecrawl-mcp-server)
