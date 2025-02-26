"""GraphQL formatters and example generators.

Utilities for formatting GraphQL types and generating example operation strings.
"""

from typing import Any, Dict, List


def format_type_info(type_info: Dict[str, Any]) -> str:
    """Format GraphQL type information into a readable string.

    Takes a GraphQL type object and converts it into a human-readable type string,
    handling nested types like NON_NULL and LIST.

    Args:
        type_info: Dictionary containing GraphQL type information

    Returns:
        A string representation of the type (e.g., "String!", "[User]", etc.)
    """
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


def generate_operation_example(name: str, args: List[Dict[str, Any]], operation_type: str = "query") -> str:
    """Generate an example GraphQL query or mutation string.

    Creates a formatted GraphQL operation string with variables and arguments properly structured.

    Args:
        name: The name of the operation (query or mutation)
        args: List of argument dictionaries with name, type, and other metadata
        operation_type: Either "query" or "mutation"

    Returns:
        A formatted GraphQL operation string ready to be executed
    """
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

    return f"""{operation_type} {name.capitalize()}{variables_section} {{
  {name}{args_section} {{
    # Include fields you want to retrieve
    id
    # Add more fields as needed
  }}
}}"""
