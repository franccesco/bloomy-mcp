# Bloomy MCP

A Model Context Protocol (MCP) server for interacting with Bloom Growth's GraphQL API.

## Overview

Bloomy MCP is a server that connects to Bloom Growth's GraphQL API and exposes it through the Model Context Protocol, enabling AI assistants to perform operations against the Bloom Growth platform.

## Features

- Query Bloom Growth GraphQL API through MCP
- Retrieve query and mutation details
- Execute GraphQL queries and mutations via MCP tools
- Get authenticated user information
- Automatic schema introspection

## Installation

### Prerequisites

- Python 3.12 or higher
- Access to Bloom Growth API

### Setup

1. Clone this repository
2. Set up a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Environment Variables

Create a `.env` file with the following variables:

```
BLOOM_API_URL=<Your Bloom API URL>
BLOOM_API_TOKEN=<Your Bloom API Token>
```

## Usage

### Running the Server

Start the Bloomy MCP server:

```bash
bloomy-server
```

### Available MCP Tools

The following MCP tools are available for AI assistants:

- `get_query_details` - Get detailed information about specific GraphQL queries
- `get_mutation_details` - Get detailed information about specific GraphQL mutations
- `execute_query` - Execute a GraphQL query or mutation with variables
- `get_authenticated_user_id` - Get the ID of the currently authenticated user

### Available MCP Resources

- `bloom://queries` - Get a list of all available queries
- `bloom://mutations` - Get a list of all available mutations

## Development

### Project Structure

```
src/
  └── bloomy_mcp/
      ├── __init__.py        # Package initialization
      ├── client.py          # GraphQL client implementation
      ├── formatters.py      # Data formatting utilities
      ├── introspection.py   # GraphQL schema introspection
      ├── operations.py      # GraphQL operation utilities
      └── server.py          # MCP server implementation
```

### Dependencies

- `mcp[cli]` - Model Context Protocol server
- `gql` - GraphQL client library
- `httpx` - HTTP client
- `pyyaml` - YAML processing

## License

[License Information]

## Contact

[Contact Information]
