import dwellir_harvester.lib as lib


def test_lib_exports_core_symbols():
    assert lib.CollectorBase
    assert lib.GenericCollector
    assert lib.BlockchainCollector
    assert lib.CollectResult
    assert lib.validate_output
    assert lib.load_collectors


def test_bundled_schema_path_exists():
    path = lib.bundled_schema_path()
    assert path and isinstance(path, str)
