"""RPC client functions for Substrate-based blockchains."""

from __future__ import annotations
from typing import Optional, Tuple, Any

from dwellir_harvester.rpc_common import jsonrpc_call


def rpc_get_system_version(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Get the Substrate system version via RPC.
    
    Args:
        url: The URL of the Substrate node's RPC endpoint
        
    Returns:
        A tuple of (version, error) where only one will be non-None
    """
    res, err = jsonrpc_call(url, "system_version")
    if res is None:
        return None, err
    try:
        return str(res), None
    except Exception as e:
        return None, f"rpc system_version parse error for {res!r}: {e}"


def rpc_get_system_name(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Get the Substrate system name via RPC.
    
    Args:
        url: The URL of the Substrate node's RPC endpoint
        
    Returns:
        A tuple of (name, error) where only one will be non-None
    """
    res, err = jsonrpc_call(url, "system_name")
    if res is None:
        return None, err
    try:
        return str(res), None
    except Exception as e:
        return None, f"rpc system_name parse error for {res!r}: {e}"


def rpc_get_system_chain(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Get the Substrate chain name via RPC.
    
    Args:
        url: The URL of the Substrate node's RPC endpoint
        
    Returns:
        A tuple of (chain_name, error) where only one will be non-None
    """
    res, err = jsonrpc_call(url, "system_chain")
    if res is None:
        return None, err
    try:
        return str(res), None
    except Exception as e:
        return None, f"rpc system_chain parse error for {res!r}: {e}"


def rpc_get_genesis_hash(url: str) -> Tuple[Optional[str], Optional[str]]:
    """Get the Substrate genesis block hash via RPC.
    
    Args:
        url: The URL of the Substrate node's RPC endpoint
        
    Returns:
        A tuple of (genesis_hash, error) where only one will be non-None
    """
    res, err = jsonrpc_call(url, "chain_getBlockHash", [0])
    if res is None:
        return None, err
    try:
        return str(res), None
    except Exception as e:
        return None, f"rpc chain_getBlockHash parse error for {res!r}: {e}"
