"""RPC client functions for EVM-compatible blockchains."""

from __future__ import annotations
from typing import Optional, Tuple, Any, Dict

from dwellir_harvester.rpc_common import jsonrpc_call


def rpc_get_client_version(url: str, timeout: float = 2.5) -> Tuple[Optional[str], Optional[str]]:
    """Get the client version via RPC.
    
    Args:
        url: The URL of the node's RPC endpoint
        timeout: Request timeout in seconds
        
    Returns:
        A tuple of (version, error) where only one will be non-None
    """
    return jsonrpc_call(url, "web3_clientVersion", timeout=timeout)


def rpc_get_chain_id(url: str, timeout: float = 2.5) -> Tuple[Optional[int], Optional[str]]:
    """Get the chain ID via RPC.
    
    Args:
        url: The URL of the node's RPC endpoint
        timeout: Request timeout in seconds
        
    Returns:
        A tuple of (chain_id, error) where only one will be non-None
    """
    res, err = jsonrpc_call(url, "eth_chainId", timeout=timeout)
    if res is None:
        return None, err
    try:
        # Convert hex string to int
        return int(res, 16), None
    except (ValueError, TypeError) as e:
        return None, f"rpc eth_chainId parse error for {res!r}: {e}"


def rpc_get_net_version(url: str, timeout: float = 2.5) -> Tuple[Optional[str], Optional[str]]:
    """Get the network version via RPC.
    
    Args:
        url: The URL of the node's RPC endpoint
        timeout: Request timeout in seconds
        
    Returns:
        A tuple of (net_version, error) where only one will be non-None
    """
    res, err = jsonrpc_call(url, "net_version", timeout=timeout)
    if res is None:
        return None, err
    try:
        return str(res), None
    except Exception as e:
        return None, f"rpc net_version parse error for {res!r}: {e}"


def map_network_name(chain_id: Optional[int], net_version: Optional[str]) -> str:
    """Map chain ID and net version to a human-readable network name.
    
    Args:
        chain_id: The chain ID from eth_chainId
        net_version: The network version from net_version
        
    Returns:
        A human-readable network name or "unknown"
    """
    if chain_id is not None:
        # Common chain IDs
        if chain_id == 1:
            return "Ethereum Mainnet"
        elif chain_id == 3:
            return "Ropsten Testnet"
        elif chain_id == 4:
            return "Rinkeby Testnet"
        elif chain_id == 5:
            return "Goerli Testnet"
        elif chain_id == 42:
            return "Kovan Testnet"
        elif chain_id == 11155111:
            return "Sepolia Testnet"
        elif chain_id == 10:
            return "Optimism"
        elif chain_id == 100:
            return "Gnosis Chain (xDai)"
        elif chain_id == 137:
            return "Polygon Mainnet"
    
    if net_version is not None:
        # Fallback to net_version if chain_id is not available
        if net_version == "1":
            return "Ethereum Mainnet"
        elif net_version == "3":
            return "Ropsten Testnet"
        elif net_version == "4":
            return "Rinkeby Testnet"
        elif net_version == "5":
            return "Goerli Testnet"
        elif net_version == "42":
            return "Kovan Testnet"
        elif net_version == "11155111":
            return "Sepolia Testnet"
    
    return "unknown"
