"""GraphQL client for Bloom API.

Provides a client for connecting to and executing operations against the Bloom GraphQL API.
"""

from os import getenv
from typing import Any, Dict, Optional

from gql import Client as GQLClient, gql
from gql.transport.httpx import HTTPXTransport

# API configuration
BLOOM_API_URL = getenv("BLOOM_API_URL")
BLOOM_API_TOKEN = getenv("BLOOM_API_TOKEN")


class Client:
    """Client for interacting with the Bloom GraphQL API."""

    def __init__(self) -> None:
        """Initialize the GraphQL client with authentication.

        Uses environment variables BLOOM_API_URL and BLOOM_API_TOKEN for configuration.
        """
        headers = {"Authorization": f"Bearer {BLOOM_API_TOKEN}"}
        transport = HTTPXTransport(url=BLOOM_API_URL, headers=headers)
        self.gql_client = GQLClient(transport=transport, fetch_schema_from_transport=True)

    def execute(self, query: Any, variable_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query or mutation.

        Args:
            query: The GraphQL query object (created using gql())
            variable_values: Optional dictionary of variables to include with the query

        Returns:
            Dict containing the query results
        """
        return self.gql_client.execute(query, variable_values=variable_values)


# Default client instance for convenience
default_client = Client()
