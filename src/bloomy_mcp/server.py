#!/usr/bin/env python3
"""Bloom GraphQL MCP Server.

This server connects to Bloom Growth's GraphQL API and exposes it through
the Model Context Protocol (MCP).
"""

from os import getenv
from mcp.server.fastmcp import FastMCP
from gql import Client as GQLClient, gql
from gql.transport.httpx import HTTPXTransport

BLOOM_API_URL = getenv("BLOOM_API_URL")
BLOOM_API_TOKEN = getenv("BLOOM_API_TOKEN")


class Client:
    def __init__(self):
        headers = {"Authorization": f"Bearer {BLOOM_API_TOKEN}"}
        transport = HTTPXTransport(url=BLOOM_API_URL, headers=headers)
        self.gql_client = GQLClient(transport=transport, fetch_schema_from_transport=True)

    def execute(self, query, variable_values=None):
        return self.gql_client.execute(query, variable_values=variable_values)


# Initialize FastMCP server
dependencies = [
    "gql",
    "httpx",
]
mcp = FastMCP("bloom-graphql", dependencies=dependencies)

client = Client()


# Add an addition tool
@mcp.tool()
def execute_query(query: str):
    """Execute a GraphQL query"""
    query = gql(query)
    return client.execute(query)


def main():
    """Entry point for the server when run as a package."""
    # Initialize and run the server
    mcp.run()


if __name__ == "__main__":
    # Initialize and run the server
    main()
