"""
Security validation helpers for Tezos MCP server.

Provides input validation to prevent injection attacks and ensure data integrity.
"""

import re
from typing import Literal

# Tezos address patterns (official format validation)
ADDRESS_PATTERNS = {
    "tz1": re.compile(r"^tz1[1-9A-HJ-NP-Za-km-z]{33}$"),  # ed25519
    "tz2": re.compile(r"^tz2[1-9A-HJ-NP-Za-km-z]{33}$"),  # secp256k1
    "tz3": re.compile(r"^tz3[1-9A-HJ-NP-Za-km-z]{33}$"),  # p256
    "KT1": re.compile(r"^KT1[1-9A-HJ-NP-Za-km-z]{33}$"),  # contract
}

# Allowed networks (whitelist)
ALLOWED_NETWORKS = {"mainnet", "shadownet", "ghostnet"}

# Operation hash pattern
OPERATION_HASH_PATTERN = re.compile(r"^o[1-9A-HJ-NP-Za-km-z]{50}$")


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


def validate_address(address: str) -> str:
    """
    Validate a Tezos address format.

    Args:
        address: Address to validate

    Returns:
        The validated address

    Raises:
        ValidationError: If address format is invalid
    """
    if not address or not isinstance(address, str):
        raise ValidationError("address must be a non-empty string")

    # Check if matches any valid pattern
    for addr_type, pattern in ADDRESS_PATTERNS.items():
        if pattern.match(address):
            return address

    raise ValidationError(
        f"invalid tezos address format. must be tz1, tz2, tz3, or KT1 address. got: {address[:20]}..."
    )


def validate_network(network: str) -> str:
    """
    Validate network parameter against whitelist.

    Args:
        network: Network name to validate

    Returns:
        The validated network name

    Raises:
        ValidationError: If network is not in whitelist
    """
    if not network or not isinstance(network, str):
        raise ValidationError("network must be a non-empty string")

    network = network.lower().strip()

    if network not in ALLOWED_NETWORKS:
        raise ValidationError(
            f"invalid network. allowed: {', '.join(sorted(ALLOWED_NETWORKS))}. got: {network}"
        )

    return network


def validate_limit(limit: int, max_limit: int = 100) -> int:
    """
    Validate limit parameter for queries.

    Args:
        limit: Limit value to validate
        max_limit: Maximum allowed limit

    Returns:
        The validated limit

    Raises:
        ValidationError: If limit is out of bounds
    """
    if not isinstance(limit, int):
        raise ValidationError(f"limit must be an integer. got type: {type(limit).__name__}")

    if limit < 1:
        raise ValidationError(f"limit must be positive. got: {limit}")

    if limit > max_limit:
        raise ValidationError(f"limit too large. maximum: {max_limit}. got: {limit}")

    return limit


def validate_amount(amount: int, max_amount: int = 1_000_000_000_000) -> int:
    """
    Validate amount/balance in mutez.

    Args:
        amount: Amount in mutez to validate
        max_amount: Maximum allowed amount (default: 1M XTZ)

    Returns:
        The validated amount

    Raises:
        ValidationError: If amount is out of bounds
    """
    if not isinstance(amount, int):
        raise ValidationError(f"amount must be an integer. got type: {type(amount).__name__}")

    if amount < 0:
        raise ValidationError(f"amount cannot be negative. got: {amount}")

    if amount > max_amount:
        raise ValidationError(
            f"amount too large. maximum: {max_amount} mutez ({max_amount / 1_000_000} XTZ). got: {amount}"
        )

    return amount


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error message to prevent information disclosure.

    Args:
        error: Exception to sanitize

    Returns:
        Safe error message for user display
    """
    error_str = str(error)

    # Remove any potential file paths
    error_str = re.sub(r'["\']?[A-Za-z]:[\\\/][^"\']*["\']?', '[PATH]', error_str)
    error_str = re.sub(r'["\']?\/[^"\']*["\']?', '[PATH]', error_str)

    # Remove potential private keys (any base58 strings longer than 50 chars)
    error_str = re.sub(r'\b[1-9A-HJ-NP-Za-km-z]{50,}\b', '[REDACTED]', error_str)

    # Remove potential URLs with credentials
    error_str = re.sub(r'https?://[^:]+:[^@]+@[^\s]+', 'https://[REDACTED]', error_str)

    # Truncate if too long
    if len(error_str) > 200:
        error_str = error_str[:200] + "..."

    return error_str


def sanitize_log_message(message: str) -> str:
    """
    Sanitize log message to prevent private key leakage.

    Args:
        message: Log message to sanitize

    Returns:
        Safe message for logging
    """
    # Redact potential private keys
    message = re.sub(r'\bedsk[1-9A-HJ-NP-Za-km-z]{50,}\b', 'edsk[REDACTED]', message)
    message = re.sub(r'\bspsk[1-9A-HJ-NP-Za-km-z]{50,}\b', 'spsk[REDACTED]', message)
    message = re.sub(r'\bp2sk[1-9A-HJ-NP-Za-km-z]{50,}\b', 'p2sk[REDACTED]', message)

    # Redact potential seed phrases (12+ words)
    words = message.split()
    if len(words) >= 12:
        message = re.sub(r'\b[a-z]{3,}\s+[a-z]{3,}\s+[a-z]{3,}\s+[a-z]{3,}(?:\s+[a-z]{3,}){8,}\b', '[MNEMONIC]', message, flags=re.IGNORECASE)

    return message
