from __future__ import annotations
from unittest.mock import patch

from blockchain_collector.core import load_collectors, run_collector, bundled_schema_path


def test_discovery_substrate_variants_registered():
    names = set(load_collectors().keys())
    assert "polkadot" in names
    assert "ajuna" in names


def _mock_jsonrpc(url: str, method: str, params=None, timeout: float = 2.5):
    if method == "system_version":
        return "polkadot/v1.2.3", None
    if method == "system_chain":
        return "Kusama", None
    if method == "chain_getBlockHash":
        return "0xb0a8d493285c2df73290dfb7e61f870f17b41801197a149ca93654499ea3dafe", None
    return None, f"unexpected method {method}"


@patch("blockchain_collector.collectors._substrate_common._jsonrpc", side_effect=_mock_jsonrpc)
def test_run_substrate_polkadot_success(mock_rpc):
    data = run_collector(
        collector_name="polkadot",
        schema_path=bundled_schema_path(),
        validate=True,
    )
    assert data["metadata"]["collector_name"] == "polkadot"
    assert data["metadata"]["last_collect_status"] == "success"
    assert data["blockchain"]["blockchain_ecosystem"] == "Polkadot"
    assert data["blockchain"]["blockchain_network_name"] == "Kusama"
    assert data["workload"]["client_name"] == "polkadot"
    assert data["workload"]["client_version"].startswith("polkadot/")


def _mock_jsonrpc_ajuna(url: str, method: str, params=None, timeout: float = 2.5):
    if method == "system_version":
        return "ajuna-node/0.8.9", None
    if method == "system_chain":
        return "Ajuna", None
    if method == "chain_getBlockHash":
        return "0x1111111111111111111111111111111111111111111111111111111111111111", None
    return None, f"unexpected method {method}"


@patch("blockchain_collector.collectors._substrate_common._jsonrpc", side_effect=_mock_jsonrpc_ajuna)
def test_run_substrate_ajuna_success(mock_rpc):
    data = run_collector(
        collector_name="ajuna",
        schema_path=bundled_schema_path(),
        validate=True,
    )
    assert data["metadata"]["collector_name"] == "ajuna"
    assert data["metadata"]["last_collect_status"] == "success"
    assert data["blockchain"]["blockchain_ecosystem"] == "Polkadot"
    assert data["blockchain"]["blockchain_network_name"] == "Ajuna"
    assert data["workload"]["client_name"] == "ajuna-node"
    assert data["workload"]["client_version"].startswith("ajuna-node/")
