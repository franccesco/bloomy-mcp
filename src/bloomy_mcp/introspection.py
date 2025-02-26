"""GraphQL schema introspection utilities.

Functions for querying and extracting information from the GraphQL schema.
"""

from typing import List

from gql import gql

from bloomy_mcp.client import default_client


def get_available_queries() -> str:
    """Get a list of all available GraphQL queries.

    Returns:
        A comma-separated string of all available query names
    """
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

    result = default_client.execute(queries_list_query)

    # Create a simple comma-separated list of query names
    query_names = [field["name"] for field in result["__schema"]["queryType"]["fields"]]
    return ", ".join(query_names)


def get_available_mutations() -> str:
    """Get a list of all available GraphQL mutations.

    Returns:
        A comma-separated string of all available mutation names
    """
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

    result = default_client.execute(mutations_list_query)

    # Create a simple comma-separated list of mutation names
    mutation_names = [field["name"] for field in result["__schema"]["mutationType"]["fields"]]
    return ", ".join(mutation_names)


def get_available_operation_names(operation_type: str) -> List[str]:
    """Get a list of all available operation names for a given type.

    Args:
        operation_type: Either "query" or "mutation"

    Returns:
        List of available operation names
    """
    if operation_type == "query":
        operations_str = get_available_queries()
    else:
        operations_str = get_available_mutations()

    return [name.strip() for name in operations_str.split(",")]
