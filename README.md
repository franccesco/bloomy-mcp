# Bloom GraphQL MCP Server

An MCP server that connects to Bloom Growth's GraphQL API and exposes it through the Model Context Protocol.

## Features

- 🔌 Connects to Bloom Growth's GraphQL endpoint
- 📃 Exposes GraphQL schema as resources
- 🔍 Provides tools for running queries
- ✏️ Provides tools for executing mutations
- 🔐 Securely authenticates with bearer token

## Installation

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file with your Bloom Growth API token:

```
BLOOM_API_TOKEN=your_api_token_here
```

## Usage

```bash
# Start the server
mcp dev src/bloomy_mcp/server.py
```

Or integrate with Claude Desktop by editing your `claude_desktop_config.json` file to include:

```json
{
  "mcpServers": {
    "bloom-graphql": {
      "command": "python",
      "args": ["-m", "bloomy_mcp.server"],
      "env": {
        "BLOOM_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

## Development

To add new features or fix bugs:

1. Make your changes
2. Test with `mcp dev src/bloomy_mcp/server.py`
3. Use the MCP Inspector to verify functionality
