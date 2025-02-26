#!/usr/bin/env python3
"""Bloom GraphQL MCP Server.

This server connects to Bloom Growth's GraphQL API and exposes it through
the Model Context Protocol (MCP).
"""

from os import getenv
from mcp.server.fastmcp import FastMCP
from gql import Client as GQLClient, gql
from gql.transport.httpx import HTTPXTransport
import yaml

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
    "pyyaml",
]
mcp = FastMCP("bloom-graphql", dependencies=dependencies)

client = Client()


# Query operation resources
@mcp.resource("bloom://queries")
def get_available_queries():
    """Get a list of all available GraphQL queries"""
    queries_list_query = gql(
        """
    {
      __schema {
        queryType {
          name
          fields {
            name
            description
          }
        }
      }
    }
    """
    )

    result = client.execute(queries_list_query)

    # Create a simple comma-separated list of query names
    query_names = [field["name"] for field in result["__schema"]["queryType"]["fields"]]
    return ", ".join(query_names)


@mcp.resource("bloom://mutations")
def get_available_mutations():
    """Get a list of all available GraphQL mutations"""
    mutations_list_query = gql(
        """
    {
      __schema {
        mutationType {
          name
          fields {
            name
            description
          }
        }
      }
    }
    """
    )

    result = client.execute(mutations_list_query)

    # Create a simple comma-separated list of mutation names
    mutation_names = [field["name"] for field in result["__schema"]["mutationType"]["fields"]]
    return ", ".join(mutation_names)


# Tools for getting operation details and execution
@mcp.tool()
def get_query_details(query_name: str):
    """Get detailed information about a specific query including required arguments and return type structure"""
    query_details_query = gql(
        """
    {
      __type(name: "QueryType") {
        fields(includeDeprecated: false) {
          name
          description
          args {
            name
            description
            type {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
            defaultValue
          }
          type {
            kind
            name
            ofType {
              kind
              name
            }
          }
        }
      }
    }
    """
    )

    try:
        result = client.execute(query_details_query)

        # Find the specific query
        query_info = None
        for field in result["__type"]["fields"]:
            if field["name"] == query_name:
                query_info = field
                break

        if not query_info:
            return f"Query '{query_name}' not found"

        # Format arguments
        args = []
        for arg in query_info["args"]:
            type_info = format_type_info(arg["type"])
            args.append(
                {
                    "name": arg["name"],
                    "description": arg["description"] or "No description",
                    "type": type_info,
                    "required": type_info.endswith("!"),
                    "defaultValue": arg["defaultValue"],
                }
            )

        # Format return type
        return_type = format_type_info(query_info["type"])

        # Create result structure
        details = {
            "name": query_name,
            "description": query_info["description"] or "No description",
            "arguments": args,
            "returnType": return_type,
            "example": generate_query_example(query_name, args),
        }

        return yaml.dump(details, sort_keys=False)

    except Exception as e:
        return f"Error getting query details: {str(e)}"


@mcp.tool()
def get_mutation_details(mutation_name: str):
    """Get detailed information about a specific mutation including required arguments and return type structure"""
    mutation_details_query = gql(
        """
    {
      __type(name: "MutationType") {
        fields(includeDeprecated: false) {
          name
          description
          args {
            name
            description
            type {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
            defaultValue
          }
          type {
            kind
            name
            ofType {
              kind
              name
            }
          }
        }
      }
    }
    """
    )

    try:
        result = client.execute(mutation_details_query)

        # Find the specific mutation
        mutation_info = None
        for field in result["__type"]["fields"]:
            if field["name"] == mutation_name:
                mutation_info = field
                break

        if not mutation_info:
            return f"Mutation '{mutation_name}' not found"

        # Format arguments
        args = []
        for arg in mutation_info["args"]:
            type_info = format_type_info(arg["type"])
            args.append(
                {
                    "name": arg["name"],
                    "description": arg["description"] or "No description",
                    "type": type_info,
                    "required": type_info.endswith("!"),
                    "defaultValue": arg["defaultValue"],
                }
            )

        # Format return type
        return_type = format_type_info(mutation_info["type"])

        # Create result structure
        details = {
            "name": mutation_name,
            "description": mutation_info["description"] or "No description",
            "arguments": args,
            "returnType": return_type,
            "example": generate_mutation_example(mutation_name, args),
        }

        return yaml.dump(details, sort_keys=False)

    except Exception as e:
        return f"Error getting mutation details: {str(e)}"


@mcp.tool()
def execute_query(query: str, variables: dict = None):
    """Execute a GraphQL query or mutation with variables"""
    try:
        parsed_query = gql(query)
        result = client.execute(parsed_query, variable_values=variables)
        return result
    except Exception as e:
        return f"Error executing query: {str(e)}"


# Helper functions
def format_type_info(type_info):
    """Format type information into a readable string"""
    kind = type_info.get("kind", "")
    name = type_info.get("name", "")
    of_type = type_info.get("ofType", {})

    if kind == "NON_NULL":
        inner_type = format_type_info(of_type)
        return f"{inner_type}!"
    elif kind == "LIST":
        inner_type = format_type_info(of_type)
        return f"[{inner_type}]"
    else:
        return name or "Unknown"


def generate_query_example(name, args):
    """Generate an example query string"""
    variables_section = ""
    args_section = ""

    # Generate variables section
    if args:
        var_list = []
        for arg in args:
            var_list.append(f"${arg['name']}: {arg['type']}")
        variables_section = f"({', '.join(var_list)})"

    # Generate args section
    if args:
        arg_list = []
        for arg in args:
            arg_list.append(f"{arg['name']}: ${arg['name']}")
        args_section = f"({', '.join(arg_list)})"

    return f"""query {name.capitalize()}{variables_section} {{
  {name}{args_section} {{
    # Include fields you want to retrieve
    id
    # Add more fields as needed
  }}
}}"""


def generate_mutation_example(name, args):
    """Generate an example mutation string"""
    variables_section = ""
    args_section = ""

    # Generate variables section
    if args:
        var_list = []
        for arg in args:
            var_list.append(f"${arg['name']}: {arg['type']}")
        variables_section = f"({', '.join(var_list)})"

    # Generate args section
    if args:
        arg_list = []
        for arg in args:
            arg_list.append(f"{arg['name']}: ${arg['name']}")
        args_section = f"({', '.join(arg_list)})"

    return f"""mutation {name.capitalize()}{variables_section} {{
  {name}{args_section} {{
    # Include fields you want to retrieve
    id
    # Add more fields as needed
  }}
}}"""


def main():
    """Entry point for the server when run as a package."""
    # Initialize and run the server
    mcp.run()


if __name__ == "__main__":
    # Initialize and run the server
    main()
