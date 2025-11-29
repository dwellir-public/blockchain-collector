import importlib
import sys
from pathlib import Path

import dwellir_harvester.lib as lib
from dwellir_harvester.lib import run as lib_run


class DummyCollector(lib.GenericCollector):
    NAME = "dummy_plugin_test"
    VERSION = "0.0.1"

    def collect(self):
        return {"metadata": self._get_metadata(), "data": {"ok": True}}


def test_filesystem_plugin_loading(tmp_path: Path, monkeypatch):
    # Write a plugin module to a temp directory
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "dummy_plugin.py"
    plugin_file.write_text(
        "from dwellir_harvester.collector_base import GenericCollector\n"
        "class DummyPlugin(GenericCollector):\n"
        "    NAME='dummy_plugin_test'\n"
        "    VERSION='0.0.1'\n"
        "    def collect(self):\n"
        "        return {'ok': True}\n"
    )

    # Load with plugin path
    mapping = lib.load_collectors(plugin_paths=[str(plugin_dir)])
    assert "dummy_plugin_test" in mapping
    cls = mapping["dummy_plugin_test"]
    inst = cls()
    res = inst.run()
    assert res["data"]["ok"] is True


def test_entry_point_hook(monkeypatch):
    # Simulate entry point discovery by patching importlib.metadata.entry_points
    class DummyEP:
        name = "dummy_plugin_test_ep"

        def load(self):
            return DummyCollector

    def fake_eps():
        return {"dwellir_harvester.collectors": [DummyEP()]}

    monkeypatch.setattr(importlib.metadata, "entry_points", fake_eps)

    mapping = lib.load_collectors()
    assert "dummy_plugin_test" in mapping or "dummy_plugin_test_ep" in mapping


def test_lib_runner_with_temp_plugin(tmp_path: Path, capsys):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "runner_plugin.py"
    plugin_file.write_text(
        "from dwellir_harvester.collector_base import GenericCollector\n"
        "class RunnerPlugin(GenericCollector):\n"
        "    NAME='runner_plugin'\n"
        "    VERSION='0.0.1'\n"
        "    @classmethod\n"
        "    def create(cls, **kwargs):\n"
        "        return cls(**kwargs)\n"
        "    def collect(self):\n"
        "        return {'msg': 'runner ok'}\n"
    )

    rc = lib_run.main(["runner_plugin:RunnerPlugin", "--collector-path", str(plugin_dir)])
    captured = capsys.readouterr()
    assert rc == 0
    assert '"msg": "runner ok"' in captured.out
