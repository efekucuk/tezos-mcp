"""
Tezos MCP Server - Read-Only Version (No PyTezos Required)

This version provides read-only blockchain queries without requiring PyTezos.
Perfect for testing on Windows without build tools.
"""

import logging
import os
from decimal import Decimal

from mcp.server.fastmcp import FastMCP
import httpx

from security import (
    validate_address,
    validate_network,
    validate_limit,
    sanitize_error_message,
    ValidationError
)

# Configure logging to stderr (required for STDIO transport)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("tezos-readonly")

# Default RPC nodes for different networks (Official endpoints from https://teztnets.com/)
DEFAULT_NODES = {
    "mainnet": "https://mainnet.api.tez.ie",
    "shadownet": "https://rpc.shadownet.teztnets.com",
    "ghostnet": "https://rpc.ghostnet.teztnets.com",
}


def format_tez(mutez: int) -> str:
    """Convert mutez to tez with proper formatting."""
    tez = Decimal(mutez) / Decimal(1_000_000)
    return f"{tez:,.6f} XTZ"


@mcp.tool()
async def get_balance(address: str, network: str = "mainnet") -> str:
    """
    Get the XTZ balance of a Tezos address (read-only, no private key required).

    Args:
        address: Tezos address (tz1, tz2, tz3, or KT1)
        network: Network to query (mainnet, shadownet, ghostnet)

    Returns:
        Account balance in XTZ
    """
    try:
        # validate inputs
        address = validate_address(address)
        network = validate_network(network)

        node_url = DEFAULT_NODES.get(network, DEFAULT_NODES["mainnet"])
        # check for custom node in env (already validated network name)
        custom_node = os.getenv(f"TEZOS_{network.upper()}_NODE")
        if custom_node:
            node_url = custom_node

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{node_url}/chains/main/blocks/head/context/contracts/{address}/balance"
            )
            response.raise_for_status()

            # Parse balance (RPC returns quoted string)
            balance_str = response.text.strip().strip('"')
            balance_mutez = int(balance_str)
            balance_tez = format_tez(balance_mutez)

            return f"Address: {address}\nNetwork: {network}\nBalance: {balance_tez}"

    except ValidationError as e:
        return f"validation error: {str(e)}"
    except httpx.HTTPError as e:
        logger.error(f"HTTP error getting balance: {e}")
        return f"error: http request failed"
    except ValueError as e:
        logger.error(f"Error parsing balance: {e}")
        return f"error: invalid balance format"
    except Exception as e:
        logger.error(f"Error getting balance: {e}")
        return f"error: {sanitize_error_message(e)}"


@mcp.tool()
async def get_operations(address: str, limit: int = 10, network: str = "mainnet") -> str:
    """
    Get recent operations (transactions) for a Tezos address.

    Args:
        address: Tezos address to query
        limit: Maximum number of operations to return (default: 10)
        network: Network to query (mainnet, shadownet, ghostnet)

    Returns:
        List of recent operations
    """
    try:
        # validate inputs
        address = validate_address(address)
        network = validate_network(network)
        limit = validate_limit(limit, max_limit=100)

        # Use TzKT API for better operation history
        tzkt_urls = {
            "mainnet": "https://api.tzkt.io",
            "shadownet": "https://api.shadownet.tzkt.io",
            "ghostnet": "https://api.ghostnet.tzkt.io",
        }

        tzkt_url = tzkt_urls.get(network, tzkt_urls["mainnet"])

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{tzkt_url}/v1/accounts/{address}/operations",
                params={"limit": limit, "type": "transaction"}
            )
            response.raise_for_status()
            operations = response.json()

        if not operations:
            return f"no recent operations found for {address} on {network}"

        result = f"recent operations for {address} on {network}:\n\n"
        for i, op in enumerate(operations[:limit], 1):
            amount = format_tez(op.get('amount', 0))
            result += f"{i}. hash: {op.get('hash')}\n"
            result += f"   type: {op.get('type')}\n"
            result += f"   from: {op.get('sender', {}).get('address', 'N/A')}\n"
            result += f"   to: {op.get('target', {}).get('address', 'N/A')}\n"
            result += f"   amount: {amount}\n"
            result += f"   status: {op.get('status')}\n"
            result += f"   timestamp: {op.get('timestamp')}\n\n"

        return result

    except ValidationError as e:
        return f"validation error: {str(e)}"
    except httpx.HTTPError as e:
        logger.error(f"HTTP error getting operations: {e}")
        return f"error: http request failed"
    except Exception as e:
        logger.error(f"Error getting operations: {e}")
        return f"error: {sanitize_error_message(e)}"


@mcp.tool()
async def get_block_info(level: int | None = None, network: str = "mainnet") -> str:
    """
    Get information about a specific block or the latest block.

    Args:
        level: Block level/height (optional, defaults to latest)
        network: Network to query (mainnet, shadownet, ghostnet)

    Returns:
        Block information including hash, level, timestamp, and baker
    """
    try:
        # validate inputs
        network = validate_network(network)
        if level is not None:
            if not isinstance(level, int) or level < 0:
                raise ValidationError(f"block level must be a non-negative integer, got: {level}")

        node_url = DEFAULT_NODES.get(network, DEFAULT_NODES["mainnet"])
        custom_node = os.getenv(f"TEZOS_{network.upper()}_NODE")
        if custom_node:
            node_url = custom_node

        if level is None:
            url = f"{node_url}/chains/main/blocks/head/header"
        else:
            url = f"{node_url}/chains/main/blocks/{level}/header"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            block = response.json()

        return f"""block information ({network}):
level: {block['level']}
hash: {block['hash']}
timestamp: {block['timestamp']}
baker: {block.get('baker', block.get('payload_producer', 'N/A'))}
protocol: {block['protocol']}
"""

    except ValidationError as e:
        return f"validation error: {str(e)}"
    except httpx.HTTPError as e:
        logger.error(f"HTTP error getting block info: {e}")
        return f"error: http request failed"
    except Exception as e:
        logger.error(f"Error getting block info: {e}")
        return f"error: {sanitize_error_message(e)}"


@mcp.tool()
async def get_network_info(network: str = "mainnet") -> str:
    """
    Get information about the Tezos network.

    Args:
        network: Network to query (mainnet, shadownet, ghostnet)

    Returns:
        Network constants and protocol information
    """
    try:
        # validate inputs
        network = validate_network(network)

        node_url = DEFAULT_NODES.get(network, DEFAULT_NODES["mainnet"])
        custom_node = os.getenv(f"TEZOS_{network.upper()}_NODE")
        if custom_node:
            node_url = custom_node

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get current protocol
            head_response = await client.get(f"{node_url}/chains/main/blocks/head/header")
            head_response.raise_for_status()
            protocol = head_response.json()['protocol']

            # Get network constants
            constants_response = await client.get(f"{node_url}/chains/main/blocks/head/context/constants")
            constants_response.raise_for_status()
            constants = constants_response.json()

        return f"""tezos network information ({network}):

protocol: {protocol}
time between blocks: {constants.get('minimal_block_delay', 'N/A')} seconds
hard gas limit per operation: {constants.get('hard_gas_limit_per_operation', 'N/A')}
hard storage limit per operation: {constants.get('hard_storage_limit_per_operation', 'N/A')}
cost per byte: {constants.get('cost_per_byte', 'N/A')} mutez
consensus threshold: {constants.get('consensus_threshold', 'N/A')}
"""

    except ValidationError as e:
        return f"validation error: {str(e)}"
    except httpx.HTTPError as e:
        logger.error(f"HTTP error getting network info: {e}")
        return f"error: http request failed"
    except Exception as e:
        logger.error(f"Error getting network info: {e}")
        return f"error: {sanitize_error_message(e)}"


def main():
    """Run the Tezos MCP server (read-only version)."""
    logger.info("Starting Tezos MCP server (read-only)...")
    logger.info("This version provides read-only queries without PyTezos")
    logger.info("For full functionality including transactions, use server.py with PyTezos installed")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
