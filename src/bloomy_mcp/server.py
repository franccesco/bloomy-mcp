#!/usr/bin/env python3
"""Bloom GraphQL MCP Server.

This server connects to Bloom Growth's GraphQL API and exposes it through
the Model Context Protocol (MCP).
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

import httpx
import dotenv
from gql import Client, gql
from gql.transport.httpx import HTTPXTransport

from mcp.server.fastmcp import FastMCP, Context

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bloom-graphql-server")

# Get API token from environment
BLOOM_API_TOKEN = os.getenv("BLOOM_API_TOKEN")
if not BLOOM_API_TOKEN:
    logger.warning("BLOOM_API_TOKEN not set in environment. Requests may fail.")

# GraphQL endpoint
GRAPHQL_ENDPOINT = "https://app.bloomgrowth.com/graphql"

# Initialize FastMCP server
mcp = FastMCP("bloom-graphql")

# Initialize GraphQL client
transport = HTTPXTransport(
    url=GRAPHQL_ENDPOINT,
    headers={"Authorization": f"Bearer {BLOOM_API_TOKEN}"},
)
client = Client(transport=transport, fetch_schema_from_transport=True)


@dataclass
class GraphQLResult:
    """Structure to hold GraphQL query/mutation results."""

    data: Dict[str, Any]
    errors: Optional[List[Dict[str, Any]]] = None


class GraphQLService:
    """Service for interacting with the Bloom Growth GraphQL API."""

    @staticmethod
    async def execute_query(query: str, variables: Optional[Dict[str, Any]] = None) -> GraphQLResult:
        """Execute a GraphQL query against the Bloom Growth API.

        Args:
            query: The GraphQL query string
            variables: Optional variables for the query

        Returns:
            GraphQLResult containing data and errors if any
        """
        if not variables:
            variables = {}

        try:
            # Parse the query string
            parsed_query = gql(query)

            # Execute the query
            result = await client.execute_async(parsed_query, variable_values=variables)

            return GraphQLResult(data=result)
        except Exception as e:
            logger.error(f"Error executing GraphQL query: {e}")
            return GraphQLResult(data={}, errors=[{"message": str(e), "path": ["query_execution"]}])

    @staticmethod
    async def get_schema() -> str:
        """Retrieve the GraphQL schema from the endpoint.

        Returns:
            Schema string in SDL format
        """
        # Introspection query to get schema
        introspection_query = """
        query IntrospectionQuery {
          __schema {
            queryType {
              name
              fields {
                name
                description
                args {
                  name
                  description
                  type {
                    name
                    kind
                    ofType {
                      name
                      kind
                    }
                  }
                  defaultValue
                }
                type {
                  name
                  kind
                  ofType {
                    name
                    kind
                  }
                }
              }
            }
            mutationType {
              name
              fields {
                name
                description
                args {
                  name
                  description
                  type {
                    name
                    kind
                    ofType {
                      name
                      kind
                    }
                  }
                  defaultValue
                }
                type {
                  name
                  kind
                  ofType {
                    name
                    kind
                  }
                }
              }
            }
            types {
              name
              kind
              description
              fields {
                name
                description
                args {
                  name
                  description
                  type {
                    name
                    kind
                    ofType {
                      name
                      kind
                    }
                  }
                  defaultValue
                }
                type {
                  name
                  kind
                  ofType {
                    name
                    kind
                  }
                }
              }
              inputFields {
                name
                description
                type {
                  name
                  kind
                  ofType {
                    name
                    kind
                  }
                }
                defaultValue
              }
              interfaces {
                name
              }
              enumValues {
                name
                description
              }
              possibleTypes {
                name
              }
            }
          }
        }
        """

        try:
            result = await GraphQLService.execute_query(introspection_query)
            # Format the schema data into human-readable format
            return json.dumps(result.data["__schema"], indent=2)
        except Exception as e:
            logger.error(f"Error fetching schema: {e}")
            return f"Error fetching schema: {e}"


# MCP Resource implementations


@mcp.resource("graphql://schema")
async def get_graphql_schema() -> str:
    """Get the full GraphQL schema from Bloom Growth."""
    return await GraphQLService.get_schema()


@mcp.resource("graphql://queries")
async def get_graphql_queries() -> str:
    """Get available GraphQL queries from Bloom Growth."""
    schema = await GraphQLService.get_schema()
    schema_data = json.loads(schema)

    query_type = None
    for type_info in schema_data.get("types", []):
        if type_info.get("name") == schema_data.get("queryType", {}).get("name"):
            query_type = type_info
            break

    if not query_type:
        return "No query type found in schema"

    result = "# Available GraphQL Queries\n\n"
    for field in query_type.get("fields", []):
        result += f"## {field['name']}\n"

        if field.get("description"):
            result += f"{field['description']}\n\n"

        result += "Arguments:\n"
        for arg in field.get("args", []):
            arg_type = arg.get("type", {})
            type_name = arg_type.get("name") or arg_type.get("ofType", {}).get("name", "unknown")
            result += f"- {arg['name']}: {type_name}"
            if arg.get("description"):
                result += f" - {arg['description']}"
            result += "\n"

        return_type = field.get("type", {})
        type_name = return_type.get("name") or return_type.get("ofType", {}).get("name", "unknown")
        result += f"\nReturns: {type_name}\n\n"
        result += "---\n\n"

    return result


@mcp.resource("graphql://mutations")
async def get_graphql_mutations() -> str:
    """Get available GraphQL mutations from Bloom Growth."""
    schema = await GraphQLService.get_schema()
    schema_data = json.loads(schema)

    mutation_type = None
    for type_info in schema_data.get("types", []):
        if type_info.get("name") == schema_data.get("mutationType", {}).get("name"):
            mutation_type = type_info
            break

    if not mutation_type:
        return "No mutation type found in schema"

    result = "# Available GraphQL Mutations\n\n"
    for field in mutation_type.get("fields", []):
        result += f"## {field['name']}\n"

        if field.get("description"):
            result += f"{field['description']}\n\n"

        result += "Arguments:\n"
        for arg in field.get("args", []):
            arg_type = arg.get("type", {})
            type_name = arg_type.get("name") or arg_type.get("ofType", {}).get("name", "unknown")
            result += f"- {arg['name']}: {type_name}"
            if arg.get("description"):
                result += f" - {arg['description']}"
            result += "\n"

        return_type = field.get("type", {})
        type_name = return_type.get("name") or return_type.get("ofType", {}).get("name", "unknown")
        result += f"\nReturns: {type_name}\n\n"
        result += "---\n\n"

    return result


# MCP Tool implementations


@mcp.tool()
async def execute_query(query: str, variables: Optional[str] = None, ctx: Context = None) -> str:
    """Execute a GraphQL query against the Bloom Growth API.

    Args:
        query: The GraphQL query string
        variables: Optional JSON string containing variables for the query

    Returns:
        JSON string with the query results
    """
    # Log the request for debugging
    if ctx:
        ctx.info(f"Executing GraphQL query")

    # Parse variables if provided
    parsed_variables = {}
    if variables:
        try:
            parsed_variables = json.loads(variables)
        except json.JSONDecodeError as e:
            return f"Error parsing variables JSON: {e}"

    # Execute the query
    result = await GraphQLService.execute_query(query, parsed_variables)

    # Return formatted result
    return json.dumps({"data": result.data, "errors": result.errors}, indent=2)


@mcp.tool()
async def execute_mutation(mutation: str, variables: Optional[str] = None, ctx: Context = None) -> str:
    """Execute a GraphQL mutation against the Bloom Growth API.

    Args:
        mutation: The GraphQL mutation string
        variables: Optional JSON string containing variables for the mutation

    Returns:
        JSON string with the mutation results
    """
    # Log the request for debugging
    if ctx:
        ctx.info(f"Executing GraphQL mutation")

    # Parse variables if provided
    parsed_variables = {}
    if variables:
        try:
            parsed_variables = json.loads(variables)
        except json.JSONDecodeError as e:
            return f"Error parsing variables JSON: {e}"

    # Execute the mutation (uses the same method as query)
    result = await GraphQLService.execute_query(mutation, parsed_variables)

    # Return formatted result
    return json.dumps({"data": result.data, "errors": result.errors}, indent=2)


# MCP Prompt implementations


@mcp.prompt()
def query_builder(entity_name: str, fields: str) -> str:
    """Generate a GraphQL query for a specific entity with requested fields.

    Args:
        entity_name: The name of the entity to query (e.g., "user", "organization")
        fields: Comma-separated list of fields to include in the query
    """
    field_list = [field.strip() for field in fields.split(",")]
    formatted_fields = "\n    ".join(field_list)

    return f"""Please help me construct a GraphQL query for the Bloom Growth API.

I want to query the {entity_name} entity and retrieve the following fields:
{fields}

Here's the query structure:

```graphql
query Get{entity_name.capitalize()} {{
  {entity_name} {{
    {formatted_fields}
  }}
}}
```

Can you help me ensure this is correctly formatted and explain how to use variables if needed?"""


@mcp.prompt()
def mutation_builder(mutation_name: str, input_params: str) -> str:
    """Generate a GraphQL mutation template with specified inputs.

    Args:
        mutation_name: The name of the mutation to execute
        input_params: Description of the input parameters needed
    """
    return f"""Please help me construct a GraphQL mutation for the Bloom Growth API.

I want to execute the {mutation_name} mutation with these parameters:
{input_params}

Can you help me create a properly formatted mutation with variables?"""


def main():
    """Entry point for the server when run as a package."""
    # Initialize and run the server
    mcp.run()


if __name__ == "__main__":
    # Initialize and run the server
    main()
