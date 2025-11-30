# Dwellir Harvester: Pluginization & Charm-Friendly Architecture — Plan

## Goals
- Decouple charm development from the harvester codebase; charm authors can build collectors without vendoring the harvester.
- Provide a clean plugin mechanism (entry points and filesystem drop-ins).
- Keep a lean, stable core library (no execution flow) usable by charms/tests.

## Proposed Architecture
1) **Split into core + lib + collectors**
   - Decision (locked-in): publish a stable `dwellir-harvester-lib` for the core API (types, collector base classes, schema helpers, loader helpers; minimal deps). Charms depend on this; CLI/daemon can move faster.
   - `dwellir_harvester` (runner/CLI): CLI/daemon, plugin discovery wiring, built-in collectors.
   - `dwellir_harvester.collectors`: built-in collectors.
   - No backwards compatibility required during the split; aim for a clean design.

2) **Plugin discovery**
   - Sources: entry points (`dwellir_harvester.collectors`), filesystem plugin paths (env/CLI/config), built-ins.
   - Loader merge order (locked-in): built-ins → entry points → filesystem plugins; warn-and-override on collisions. Optional namespacing (e.g., `pkg::name`) if simple.
   - Plugin API: keep Python contract (return `Dict`/`CollectResult`), not raw JSON. Status via metadata/exception; schema validation optional (helpers in core).

3) **Charm developer workflow**
   - Minimal “collector SDK” import path from the lib for `GenericCollector`, `CollectResult`, `CollectorError`.
   - Charm ships its collector in a plugin path; harvester loads via env/config/CLI.
   - Provide a small harness to run a collector standalone (no Juju) for local testing.

4) **Testing story**
   - Unit tests for loader: built-ins, entry-point mocks, filesystem plugins, collisions.
   - Example plugin and example charm using a local plugin path.

5) **Backwards compatibility**
   - Refactor built-ins as needed; no backward compatibility guaranteed.
   - Default behavior unchanged if no plugin paths/entry points are present.

## Implementation Steps
1) **Core API extraction**
   - Publish a stable `dwellir-harvester-lib` (or `dwellir_harvester.lib`) exporting: `CollectorBase`, `GenericCollector`, `BlockchainCollector`, `CollectResult`, loader helpers, schema helpers. CLI/daemon depends on lib; charms depend on lib only.

2) **Plugin loader enhancements**
   - Add entry-point discovery (`importlib.metadata.entry_points`) for group `dwellir_harvester.collectors`.
   - Add filesystem plugin path support (env/config/CLI flag).
   - Update `load_collectors` to merge built-ins → entry points → filesystem plugins; warn on override; optional namespacing if simple.

3) **Config surface**
   - CLI/daemon: add `--collector-path` (repeatable) and `HARVESTER_COLLECTOR_PATHS` env var.
   - Allow selection/exclusion of collectors by name (and namespace if adopted).
   - Document entry-point option for packaged plugins.

4) **Examples & docs**
   - Add `examples/plugins/sample_collector.py`.
   - Docs for charm authors: implement a collector, place in plugin path, run with `--collector-path`.
   - Entry-point registration snippet in third-party `pyproject.toml`.
   - Document collector SDK import path and dict/CollectResult return contract.

5) **Charm integration guidance**
   - Charm depends on the stable lib, not the CLI/daemon.
   - Ship custom collector inside the charm; point harvester to that path.
   - Optional: helper script to run collector(s) in an action and dump JSON.

6) **Testing story**
   - Unit tests for loader (built-in, entry-point mock, FS plugins, collisions).
   - Example plugin and example charm using plugin path.
   - Testing SDK: tiny harness/helper to run a collector outside Juju/harvester, with optional fixture config.

7) **Validation**
   - Tests for loader behavior with built-in + entry-point + FS plugins.
   - Manual check: run CLI with `--collector-path ./examples/plugins` and see sample collector output.

## Open Questions
- Publish `dwellir-harvester-lib` as a separate PyPI package vs. bundled module name—decide naming and packaging up front.
- Collision namespacing: keep optional and simple; default is warn-and-override with deterministic order.
- Security/sandboxing: out of scope; document trust model.

## Phased Code Plan (incremental & testable)

### Phase 1: Core/lib surface and packaging
- Add `dwellir_harvester.lib` (and `lib/pyproject.toml` for `dwellir-harvester-lib`) exporting: `CollectorBase`, `GenericCollector`, `BlockchainCollector`, `CollectResult`, schema helpers, loader helpers.
- Update CLI/daemon to import from lib; built-ins remain in main package.
- Add minimal unit tests for lib imports.

### Phase 2: Loader refactor with plugin sources
- Implement entry-point discovery for group `dwellir_harvester.collectors`.
- Implement filesystem plugin paths (env + CLI `--collector-path`).
- Merge order: built-ins → entry points → filesystem plugins; warn on override; optional namespacing if simple.
- Add unit tests covering built-in only, entry-point mock, FS plugins, collision behavior.

### Phase 3: CLI/daemon config surface
- Add `--collector-path` (repeatable) and `HARVESTER_COLLECTOR_PATHS` env var; add include/exclude by name (and namespace if added).
- Wire loader config into CLI and daemon; add smoke/integration tests for flags/env.

### Phase 4: SDK/testing harness
- Provide a tiny runner/helper to execute a collector standalone (outside Juju/harvester), e.g., `python -m dwellir_harvester.lib.run <module:CollectorClass>`.
- Add a Testing SDK doc for charm authors; keep SDK deps minimal.
- Add example plugin under `examples/plugins/sample_collector.py` and test invoking via FS path.

### Phase 5: Docs and examples
- Document plugin contract (dict/CollectResult return, status via metadata/exception, optional schema validation).
- Add entry-point registration snippet for third-party `pyproject.toml`.
- Charm doc: depend on lib; ship collector in charm; point harvester to plugin path.

### Phase 6: Validation
- Run full test suite; manual CLI check with `--collector-path ./examples/plugins`.
- Confirm built-in collectors load by default; plugin overrides follow documented order.
