"""
Tezos MCP Server - Model Context Protocol server for Tezos blockchain interactions

Provides tools for:
- Querying blockchain state (balances, contracts, operations)
- Smart contract interactions (calls, originations)
- Wallet operations (signing, sending transactions)
"""

import logging
import os
import re
from typing import Any
from decimal import Decimal

from mcp.server.fastmcp import FastMCP
from pytezos import pytezos, Contract
from pytezos.rpc.errors import RpcError
import httpx

from security import (
    validate_address,
    validate_network,
    validate_limit,
    validate_amount,
    sanitize_error_message,
    sanitize_log_message,
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
mcp = FastMCP("tezos")

# Default RPC nodes for different networks (Official endpoints from https://teztnets.com/)
DEFAULT_NODES = {
    "mainnet": "https://mainnet.api.tez.ie",
    "shadownet": "https://rpc.shadownet.teztnets.com",  # Primary testnet (recommended)
    "ghostnet": "https://rpc.ghostnet.teztnets.com",    # Legacy testnet (being deprecated)
}


def get_pytezos_client(network: str = "mainnet", private_key: str | None = None) -> Any:
    """
    Get a PyTezos client configured for the specified network.

    Args:
        network: Network name (mainnet, shadownet, ghostnet)
        private_key: Optional private key for signing operations

    Returns:
        Configured PyTezos client

    Note: Ghostnet is being deprecated. Use shadownet for new development.
    """
    node_url = os.getenv(f"TEZOS_{network.upper()}_NODE", DEFAULT_NODES.get(network, DEFAULT_NODES["mainnet"]))

    if private_key:
        return pytezos.using(shell=node_url, key=private_key)
    return pytezos.using(shell=node_url)


def format_tez(mutez: int) -> str:
    """Convert mutez to tez with proper formatting."""
    tez = Decimal(mutez) / Decimal(1_000_000)
    return f"{tez:,.6f} ꜩ"


# =============================================================================
# BLOCKCHAIN QUERY TOOLS
# =============================================================================

@mcp.tool()
async def get_balance(address: str, network: str = "mainnet") -> str:
    """
    Get the XTZ balance of a Tezos address.

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

        client = get_pytezos_client(network)
        balance_mutez = client.account(address)['balance']
        balance_tez = format_tez(int(balance_mutez))

        return f"address: {address}\nnetwork: {network}\nbalance: {balance_tez}"

    except ValidationError as e:
        return f"validation error: {str(e)}"
    except RpcError as e:
        logger.error(sanitize_log_message(f"RPC error getting balance: {e}"))
        return f"error: rpc request failed"
    except Exception as e:
        logger.error(sanitize_log_message(f"Error getting balance: {e}"))
        return f"error: {sanitize_error_message(e)}"


@mcp.tool()
async def get_contract_storage(contract_address: str, network: str = "mainnet") -> str:
    """
    Get the current storage of a Tezos smart contract.

    Args:
        contract_address: Smart contract address (KT1...)
        network: Network to query (mainnet, shadownet, ghostnet)

    Returns:
        Current contract storage as JSON
    """
    try:
        # validate inputs
        contract_address = validate_address(contract_address)
        network = validate_network(network)

        client = get_pytezos_client(network)
        contract = client.contract(contract_address)
        storage = contract.storage()

        return f"contract: {contract_address}\nnetwork: {network}\n\nstorage:\n{storage}"

    except ValidationError as e:
        return f"validation error: {str(e)}"
    except RpcError as e:
        logger.error(sanitize_log_message(f"RPC error getting contract storage: {e}"))
        return f"error: rpc request failed"
    except Exception as e:
        logger.error(sanitize_log_message(f"Error getting contract storage: {e}"))
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
        node_url = DEFAULT_NODES.get(network, DEFAULT_NODES["mainnet"])

        # Use TzKT API for better operation history
        tzkt_urls = {
            "mainnet": "https://api.tzkt.io",
            "shadownet": "https://api.shadownet.tzkt.io",
            "ghostnet": "https://api.ghostnet.tzkt.io",
        }

        tzkt_url = tzkt_urls.get(network, tzkt_urls["mainnet"])

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{tzkt_url}/v1/accounts/{address}/operations",
                params={"limit": limit, "type": "transaction"}
            )
            response.raise_for_status()
            operations = response.json()

        if not operations:
            return f"No recent operations found for {address} on {network}"

        result = f"Recent operations for {address} on {network}:\n\n"
        for i, op in enumerate(operations[:limit], 1):
            amount = format_tez(op.get('amount', 0))
            result += f"{i}. Hash: {op.get('hash')}\n"
            result += f"   Type: {op.get('type')}\n"
            result += f"   From: {op.get('sender', {}).get('address', 'N/A')}\n"
            result += f"   To: {op.get('target', {}).get('address', 'N/A')}\n"
            result += f"   Amount: {amount}\n"
            result += f"   Status: {op.get('status')}\n"
            result += f"   Timestamp: {op.get('timestamp')}\n\n"

        return result

    except httpx.HTTPError as e:
        logger.error(f"HTTP error getting operations: {e}")
        return f"Error querying operations: {str(e)}"
    except Exception as e:
        logger.error(f"Error getting operations: {e}")
        return f"Error: {str(e)}"


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
        client = get_pytezos_client(network)

        if level is None:
            block = client.shell.head.header()
        else:
            block = client.shell.blocks[level].header()

        return f"""Block Information ({network}):
Level: {block['level']}
Hash: {block['hash']}
Timestamp: {block['timestamp']}
Baker: {block.get('baker', 'N/A')}
Priority: {block.get('priority', 'N/A')}
Operations Hash: {block.get('operations_hash', 'N/A')}
"""

    except RpcError as e:
        logger.error(f"RPC error getting block info: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error getting block info: {e}")
        return f"Error: {str(e)}"


# =============================================================================
# SMART CONTRACT INTERACTION TOOLS
# =============================================================================

@mcp.tool()
async def call_contract(
    contract_address: str,
    entry_point: str,
    parameters: str,
    amount: int = 0,
    network: str = "shadownet",
    private_key: str | None = None
) -> str:
    """
    Call a smart contract entry point (requires private key in environment).

    Args:
        contract_address: Contract address (KT1...)
        entry_point: Entry point name to call
        parameters: Parameters as Michelson expression or Python dict
        amount: Amount of XTZ to send (in mutez, default: 0)
        network: Network to use (mainnet, shadownet, ghostnet - shadownet recommended for testing)
        private_key: Private key for signing (or set TEZOS_PRIVATE_KEY env var)

    Returns:
        Operation hash and status
    """
    try:
        # validate inputs
        contract_address = validate_address(contract_address)
        network = validate_network(network)
        amount = validate_amount(amount)

        # validate entry_point is alphanumeric + underscore only
        if not entry_point or not isinstance(entry_point, str):
            raise ValidationError("entry_point must be a non-empty string")
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', entry_point):
            raise ValidationError(f"invalid entry_point format: {entry_point}")

        # Get private key from parameter or environment
        key = private_key or os.getenv("TEZOS_PRIVATE_KEY")
        if not key:
            return "error: private key required. set TEZOS_PRIVATE_KEY environment variable or pass private_key parameter."

        client = get_pytezos_client(network, key)
        contract = client.contract(contract_address)

        # Call the entry point - pytezos handles parameter validation
        operation = contract.call(entry_point, parameters).with_amount(amount)

        # Inject and wait for confirmation
        opg = operation.send()
        result = opg.hash()

        return f"""contract call successful!
operation hash: {result}
contract: {contract_address}
entry point: {entry_point}
amount: {format_tez(amount)}
network: {network}

view operation: https://tzkt.io/{result}
"""

    except ValidationError as e:
        return f"validation error: {str(e)}"
    except RpcError as e:
        logger.error(sanitize_log_message(f"RPC error calling contract: {e}"))
        return f"error: rpc request failed"
    except Exception as e:
        logger.error(sanitize_log_message(f"Error calling contract: {e}"))
        return f"error: {sanitize_error_message(e)}"


@mcp.tool()
async def originate_contract(
    code: str,
    storage: str,
    network: str = "shadownet",
    private_key: str | None = None,
    balance: int = 0
) -> str:
    """
    Originate (deploy) a new smart contract.

    Args:
        code: Michelson contract code
        storage: Initial storage as Michelson expression
        network: Network to deploy to (mainnet, shadownet, ghostnet - shadownet recommended for testing)
        private_key: Private key for signing (or set TEZOS_PRIVATE_KEY env var)
        balance: Initial balance in mutez (default: 0)

    Returns:
        Originated contract address and operation hash
    """
    try:
        # validate inputs
        network = validate_network(network)
        balance = validate_amount(balance)

        if not code or not isinstance(code, str):
            raise ValidationError("code must be a non-empty string")
        if not storage or not isinstance(storage, str):
            raise ValidationError("storage must be a non-empty string")

        key = private_key or os.getenv("TEZOS_PRIVATE_KEY")
        if not key:
            return "error: private key required. set TEZOS_PRIVATE_KEY environment variable."

        client = get_pytezos_client(network, key)

        # Originate the contract - pytezos validates Michelson syntax
        operation = client.origination(script={"code": code, "storage": storage}).with_amount(balance)
        opg = operation.send()

        # Get the originated contract address
        originated_contracts = opg.originated_contracts
        contract_address = originated_contracts[0] if originated_contracts else "unknown"

        return f"""contract originated successfully!
contract address: {contract_address}
operation hash: {opg.hash()}
network: {network}
initial balance: {format_tez(balance)}

view contract: https://tzkt.io/{contract_address}
"""

    except ValidationError as e:
        return f"validation error: {str(e)}"
    except RpcError as e:
        logger.error(sanitize_log_message(f"RPC error originating contract: {e}"))
        return f"error: rpc request failed"
    except Exception as e:
        logger.error(sanitize_log_message(f"Error originating contract: {e}"))
        return f"error: {sanitize_error_message(e)}"


# =============================================================================
# WALLET OPERATION TOOLS
# =============================================================================

@mcp.tool()
async def send_transaction(
    destination: str,
    amount_mutez: int,
    network: str = "shadownet",
    private_key: str | None = None
) -> str:
    """
    Send XTZ to another address.

    Args:
        destination: Recipient address
        amount_mutez: Amount to send in mutez (1 XTZ = 1,000,000 mutez)
        network: Network to use (mainnet, shadownet, ghostnet - shadownet recommended for testing)
        private_key: Private key for signing (or set TEZOS_PRIVATE_KEY env var)

    Returns:
        Transaction hash and status
    """
    try:
        # validate inputs
        destination = validate_address(destination)
        network = validate_network(network)
        amount_mutez = validate_amount(amount_mutez)

        key = private_key or os.getenv("TEZOS_PRIVATE_KEY")
        if not key:
            return "error: private key required. set TEZOS_PRIVATE_KEY environment variable."

        client = get_pytezos_client(network, key)

        # Send transaction
        operation = client.transaction(destination=destination, amount=amount_mutez)
        opg = operation.send()

        return f"""transaction sent successfully!
operation hash: {opg.hash()}
from: {client.key.public_key_hash()}
to: {destination}
amount: {format_tez(amount_mutez)}
network: {network}

view transaction: https://tzkt.io/{opg.hash()}
"""

    except ValidationError as e:
        return f"validation error: {str(e)}"
    except RpcError as e:
        logger.error(sanitize_log_message(f"RPC error sending transaction: {e}"))
        return f"error: rpc request failed"
    except Exception as e:
        logger.error(sanitize_log_message(f"Error sending transaction: {e}"))
        return f"error: {sanitize_error_message(e)}"


@mcp.tool()
async def generate_address(mnemonic: str | None = None) -> str:
    """
    Generate a new Tezos address (tz1) or derive from mnemonic.

    Args:
        mnemonic: Optional BIP39 mnemonic phrase (generates new random one if not provided)

    Returns:
        Public key hash (address), public key, and mnemonic (KEEP SECURE!)
    """
    try:
        from pytezos.crypto.key import Key

        if mnemonic:
            key = Key.from_mnemonic(mnemonic)
        else:
            key = Key.generate()
            mnemonic = key.mnemonic()

        return f"""New Tezos Address Generated:

Address (tz1...): {key.public_key_hash()}
Public Key: {key.public_key()}

IMPORTANT - KEEP SECURE:
Mnemonic: {mnemonic}
Private Key: {key.secret_key()}

⚠️  WARNING: Never share your private key or mnemonic!
Store them securely offline.
"""

    except Exception as e:
        logger.error(f"Error generating address: {e}")
        return f"Error generating address: {str(e)}"


@mcp.tool()
async def sign_message(message: str, private_key: str | None = None) -> str:
    """
    Sign a message with a Tezos private key.

    Args:
        message: Message to sign
        private_key: Private key for signing (or set TEZOS_PRIVATE_KEY env var)

    Returns:
        Signature and signed message hash
    """
    try:
        key = private_key or os.getenv("TEZOS_PRIVATE_KEY")
        if not key:
            return "Error: Private key required. Set TEZOS_PRIVATE_KEY environment variable."

        from pytezos.crypto.key import Key

        key_obj = Key.from_encoded_key(key)
        signature = key_obj.sign(message)

        return f"""Message signed successfully!

Message: {message}
Signature: {signature}
Signer Address: {key_obj.public_key_hash()}
"""

    except Exception as e:
        logger.error(f"Error signing message: {e}")
        return f"Error signing message: {str(e)}"


@mcp.tool()
async def verify_signature(message: str, signature: str, public_key: str) -> str:
    """
    Verify a signed message.

    Args:
        message: Original message
        signature: Signature to verify
        public_key: Public key of the signer

    Returns:
        Verification result
    """
    try:
        from pytezos.crypto.key import Key

        key = Key.from_encoded_key(public_key)
        is_valid = key.verify(signature, message)

        if is_valid:
            return f"✓ Signature is VALID\n\nMessage: {message}\nSigner: {key.public_key_hash()}"
        else:
            return f"✗ Signature is INVALID\n\nMessage: {message}"

    except Exception as e:
        logger.error(f"Error verifying signature: {e}")
        return f"Error verifying signature: {str(e)}"


# =============================================================================
# NETWORK & UTILITY TOOLS
# =============================================================================

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
        client = get_pytezos_client(network)

        # Get current protocol
        protocol = client.shell.head.header()['protocol']

        # Get network constants
        constants = client.shell.head.context.constants()

        return f"""Tezos Network Information ({network}):

Protocol: {protocol}
Time Between Blocks: {constants.get('minimal_block_delay', 'N/A')} seconds
Hard Gas Limit per Operation: {constants.get('hard_gas_limit_per_operation', 'N/A')}
Hard Storage Limit per Operation: {constants.get('hard_storage_limit_per_operation', 'N/A')}
Cost per Byte: {constants.get('cost_per_byte', 'N/A')} mutez
"""

    except RpcError as e:
        logger.error(f"RPC error getting network info: {e}")
        return f"Error: {str(e)}"
    except Exception as e:
        logger.error(f"Error getting network info: {e}")
        return f"Error: {str(e)}"


def main():
    """Run the Tezos MCP server."""
    logger.info("Starting Tezos MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
