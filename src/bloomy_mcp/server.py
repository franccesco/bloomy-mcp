#!/usr/bin/env python3
"""Bloom GraphQL MCP Server.

This server connects to Bloom Growth's GraphQL API and exposes it through
the Model Context Protocol (MCP).
"""

from mcp.server.fastmcp import FastMCP

from bloomy_mcp.introspection import (
    get_available_queries,
    get_available_mutations,
)
from bloomy_mcp.operations import (
    get_query_details,
    get_mutation_details,
    execute_query,
    get_authenticated_user_id,
)


# Initialize FastMCP server
dependencies = [
    "gql",
    "httpx",
    "pyyaml",
]
mcp = FastMCP("bloom-graphql", dependencies=dependencies)


# Register resources
mcp.resource("bloom://queries")(get_available_queries)
mcp.resource("bloom://mutations")(get_available_mutations)


# Register tools
mcp.tool()(get_query_details)
mcp.tool()(get_mutation_details)
mcp.tool()(execute_query)
mcp.tool()(get_authenticated_user_id)


def main() -> None:
    """Entry point for the server when run as a package.

    Initializes and runs the MCP server.
    """
    mcp.run()


if __name__ == "__main__":
    # Initialize and run the server
    main()
