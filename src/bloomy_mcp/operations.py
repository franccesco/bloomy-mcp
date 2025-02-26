"""GraphQL operation utilities.

Functions for fetching operation details and executing GraphQL operations.
"""

from typing import Any, Dict, List, Optional, Union

import yaml
from gql import gql

from bloomy_mcp.client import default_client
from bloomy_mcp.formatters import format_type_info, generate_operation_example


def get_operation_details(operation_names: str, operation_type: str) -> str:
    """Get detailed information about specific GraphQL operations.

    Retrieves and formats detailed information about GraphQL queries or mutations,
    including arguments, return types, and example usage.

    Args:
        operation_names: Comma-separated list of operation names to get details for
        operation_type: Either "query" or "mutation"

    Returns:
        A YAML-formatted string containing detailed information about the requested operations

    Raises:
        Exception: If there's an error retrieving the operation details
    """
    type_name = "QueryType" if operation_type == "query" else "MutationType"

    details_query = gql(
        f"""
    {{
      __type(name: "{type_name}") {{
        fields(includeDeprecated: false) {{
          name
          description
          args {{
            name
            description
            type {{
              kind
              name
              ofType {{
                kind
                name
                ofType {{
                  kind
                  name
                  ofType {{
                    kind
                    name
                  }}
                }}
              }}
            }}
            defaultValue
          }}
          type {{
            kind
            name
            ofType {{
              kind
              name
            }}
          }}
        }}
      }}
    }}
    """
    )

    try:
        result = default_client.execute(details_query)

        # Parse the list of operation names
        operation_name_list = [name.strip() for name in operation_names.split(",")]

        # Collect all requested operations
        all_details = {}

        for operation_name in operation_name_list:
            # Find the specific operation
            operation_info = None
            for field in result["__type"]["fields"]:
                if field["name"] == operation_name:
                    operation_info = field
                    break

            if not operation_info:
                all_details[operation_name] = f"{operation_type.capitalize()} '{operation_name}' not found"
                continue

            # Format arguments
            args = []
            for arg in operation_info["args"]:
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
            return_type = format_type_info(operation_info["type"])

            # Create result structure
            details = {
                "name": operation_name,
                "description": operation_info["description"] or "No description",
                "arguments": args,
                "returnType": return_type,
                "example": generate_operation_example(operation_name, args, operation_type),
            }

            all_details[operation_name] = details

        return yaml.dump(all_details, sort_keys=False)

    except Exception as e:
        return f"Error getting {operation_type} details: {str(e)}"


def get_query_details(query_names: str) -> str:
    """Get detailed information about specific GraphQL queries.

    Retrieves argument requirements, return type information, descriptions, and
    example usage for the specified queries.

    Args:
        query_names: Comma-separated list of query names to get details for

    Returns:
        A YAML-formatted string containing detailed information about the requested queries
    """
    return get_operation_details(query_names, "query")


def get_mutation_details(mutation_names: str) -> str:
    """Get detailed information about specific GraphQL mutations.

    Retrieves argument requirements, return type information, descriptions, and
    example usage for the specified mutations.

    Args:
        mutation_names: Comma-separated list of mutation names to get details for

    Returns:
        A YAML-formatted string containing detailed information about the requested mutations
    """
    return get_operation_details(mutation_names, "mutation")


def execute_query(query: str, variables: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], str]:
    """Execute a GraphQL query or mutation with variables.

    Parses and executes the provided GraphQL operation string with optional variables.

    Args:
        query: Raw GraphQL query or mutation string
        variables: Optional dictionary of variables to use in the operation

    Returns:
        Dictionary containing the operation results or an error message string

    Raises:
        Exception: Handled internally, returns error message as string
    """
    try:
        parsed_query = gql(query)
        result = default_client.execute(parsed_query, variable_values=variables)
        return result
    except Exception as e:
        return f"Error executing query: {str(e)}"


def get_authenticated_user_id() -> Union[str, None]:
    """Get the ID of the currently authenticated user.

    Uses a special mutation to retrieve the ID of the user associated with
    the current API token.

    Returns:
        User ID string if successful, None if user not found, or error message string

    Raises:
        Exception: Handled internally, returns error message as string
    """
    try:
        query = gql(
            """
        mutation GetAuthenticatedUserId {
            getAuthenticatedUserId
        }
        """
        )

        result = default_client.execute(query)
        return result.get("getAuthenticatedUserId")
    except Exception as e:
        return f"Error getting authenticated user ID: {str(e)}"
