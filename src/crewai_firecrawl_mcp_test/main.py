import os
import sys

from crewai import Agent
from crewai.flow import Flow, listen, start
from crewai.mcp import MCPServerHTTP, create_static_tool_filter
from pydantic import BaseModel

DEFAULT_TOPIC = "the current state of open source AI agent frameworks"


def firecrawl_mcp() -> MCPServerHTTP:
    """Hosted Firecrawl MCP server over streamable HTTP.

    The key goes in a header rather than the URL path so it stays out of the
    generated tool names. Without a key the endpoint falls back to the
    rate-limited keyless tier, which still allows search and scrape.
    """
    api_key = os.getenv("FIRECRAWL_API_KEY")

    return MCPServerHTTP(
        url="https://mcp.firecrawl.dev/v2/mcp",
        headers={"x-firecrawl-api-key": api_key} if api_key else None,
        streamable=True,
        cache_tools_list=True,
        tool_filter=create_static_tool_filter(
            allowed_tool_names=["firecrawl_search", "firecrawl_scrape"]
        ),
    )


class ResearchState(BaseModel):
    topic: str = DEFAULT_TOPIC
    findings: str = ""
    briefing: str = ""


class ResearchFlow(Flow[ResearchState]):
    """Search and read the live web, then turn the raw notes into a briefing."""

    @start()
    def gather_sources(self):
        researcher = Agent(
            role="Web Research Analyst",
            goal=f"Deliver accurate, well-sourced notes on {self.state.topic}",
            backstory=(
                "You research topics by searching the live web and reading the pages "
                "you find. You never state a claim you cannot attribute to a source "
                "you read."
            ),
            mcps=[firecrawl_mcp()],
            verbose=True,
        )

        result = researcher.kickoff(
            f"Research this topic and report what you find: {self.state.topic}\n\n"
            "Use firecrawl_search to find relevant sources, then firecrawl_scrape on "
            "the two or three most promising URLs with onlyMainContent set to true. "
            "Keep each search to at most 5 results so calls stay within the MCP tool "
            "timeout.\n\n"
            "Answer with raw notes: what each source said, each note paired with the "
            "URL it came from."
        )
        self.state.findings = result.raw

    @listen(gather_sources)
    def write_briefing(self):
        writer = Agent(
            role="Research Briefing Writer",
            goal="Turn research notes into a briefing a busy reader can act on",
            backstory=(
                "You condense raw research into short, concrete briefings. You only "
                "carry over claims that the notes attribute to a source."
            ),
            verbose=True,
        )

        result = writer.kickoff(
            f"Write a briefing on {self.state.topic} from these notes:\n\n"
            f"{self.state.findings}\n\n"
            "Answer with a one-paragraph summary followed by 3-5 key findings, each "
            "ending with the URL it came from. Drop anything the notes cannot source."
        )
        self.state.briefing = result.raw
        return result.raw


def kickoff():
    topic = " ".join(sys.argv[1:]) or os.getenv("RESEARCH_TOPIC") or DEFAULT_TOPIC
    print(f"Researching: {topic}\n")
    print(ResearchFlow().kickoff(inputs={"topic": topic}))


def plot():
    ResearchFlow().plot()


if __name__ == "__main__":
    kickoff()
