from __future__ import annotations
import os
from typing import Dict, Optional, List

from ..core import CollectResult, CollectorPartialError, CollectorFailedError
from ..rpc_substrate import (
    rpc_get_system_version,
    rpc_get_system_name,
    rpc_get_system_chain,
    rpc_get_genesis_hash
)

SUBSTRATE_COLLECTOR_VERSION = "0.1.0"

RPC_ENV = "SUBSTRATE_RPC_URL"
DEFAULT_RPC = "http://127.0.0.1:9933"


# RPC functions have been moved to rpc_substrate.py


def collect_substrate(client_name: Optional[str] = None, rpc_env: str = RPC_ENV, default_rpc: str = DEFAULT_RPC) -> CollectResult:
    messages: List[str] = []

    rpc_url = os.environ.get(rpc_env, default_rpc)

    system_version, err_ver = rpc_get_system_version(rpc_url)
    if system_version is None:
        messages.append(err_ver or "RPC system_version unavailable")

    system_name, err_name = rpc_get_system_name(rpc_url)
    if system_name is None:
        messages.append(err_name or "RPC system_name unavailable")

    system_chain, err_chain = rpc_get_system_chain(rpc_url)
    if system_chain is None:
        messages.append(err_chain or "RPC system_chain unavailable")

    genesis_hash, err_genesis = rpc_get_genesis_hash(rpc_url)
    if genesis_hash is None:
        messages.append(err_genesis or "RPC chain_getBlockHash unavailable")

    # Derive client_name from system_name only when not provided by wrapper
    if client_name is None or not str(client_name).strip():
        if system_name is None:
            client_name = ""
        else:
            client_name = system_name

    workload: Dict = {
        "client_name": client_name,
        "client_version": system_version or "unknown",
        "rpc_url": rpc_url,
    }
    blockchain: Dict = {
        "blockchain_ecosystem": "Polkadot",
        "blockchain_network_name": system_chain or "unknown",
    }
    if genesis_hash:
        blockchain["chain_id"] = genesis_hash

    have_any_info = any([system_version, system_chain, genesis_hash, client_name])
    workload_complete = bool(system_version) and bool(client_name)
    blockchain_complete = bool(system_chain)

    if not have_any_info:
        raise CollectorFailedError("; ".join(messages) or "no RPC info from node")

    if not (workload_complete and blockchain_complete):
        partial = CollectResult(blockchain=blockchain, workload=workload)
        if not bool(system_version):
            messages.append("Missing client_version (RPC system_version failed).")
        if not bool(client_name):
            messages.append("Missing client_name (RPC system_name failed and no override provided).")
        if not blockchain_complete:
            messages.append("Missing blockchain_network_name (RPC system_chain failed).")
        raise CollectorPartialError(messages or ["Partial data only."], partial=partial)

    return CollectResult(blockchain=blockchain, workload=workload)
