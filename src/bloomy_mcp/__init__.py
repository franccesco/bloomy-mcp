"""Bloom GraphQL MCP Server package.

Provides a Model Context Protocol (MCP) server for interacting with Bloom's GraphQL API.
"""

from bloomy_mcp.client import Client, default_client
from bloomy_mcp.formatters import format_type_info, generate_operation_example
from bloomy_mcp.introspection import (
    get_available_queries,
    get_available_mutations,
    get_available_operation_names,
)
from bloomy_mcp.operations import (
    get_query_details,
    get_mutation_details,
    execute_query,
    get_authenticated_user_id,
)

__all__ = [
    # Client
    "Client",
    "default_client",
    # Formatters
    "format_type_info",
    "generate_operation_example",
    # Introspection
    "get_available_queries",
    "get_available_mutations",
    "get_available_operation_names",
    # Operations
    "get_query_details",
    "get_mutation_details",
    "execute_query",
    "get_authenticated_user_id",
]
