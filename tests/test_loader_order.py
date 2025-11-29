from pathlib import Path

import dwellir_harvester.lib as lib


def test_filesystem_overrides_builtin(monkeypatch, tmp_path: Path):
    """Ensure filesystem plugins override built-ins with the same NAME."""
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "null_override.py"
    plugin_file.write_text(
        "from dwellir_harvester.collector_base import GenericCollector\n"
        "class NullOverride(GenericCollector):\n"
        "    NAME='null'\n"
        "    VERSION='9.9.9'\n"
        "    @classmethod\n"
        "    def create(cls, **kwargs):\n"
        "        return cls(**kwargs)\n"
        "    def collect(self):\n"
        "        return {'override': True}\n"
    )

    mapping = lib.load_collectors(plugin_paths=[str(plugin_dir)])

    # Built-in null exists; with override, we expect the plugin class to be loaded.
    cls = mapping.get("null")
    assert cls is not None
    assert cls.__module__ == "null_override"
    inst = cls.create()
    res = inst.run()
    assert res["data"].get("override") is True
