# Dwellir Harvester Lib Split — Plan

## Goal
Spin out a stable `dwellir-harvester-lib` repo/package for the core SDK (collector bases, helpers, loader), keeping the main `dwellir-harvester` repo for CLI/daemon and built-in collectors.

## Target Structure
- New repo: `dwellir-harvester-lib`
  - `src/dwellir_harvester/lib` (core API surface)
  - Shared core modules needed by the SDK (e.g., `collector_base.py`, result/metadata/errors, loader helpers, schema helpers, `lib.run`)
  - `pyproject.toml` with minimal deps (e.g., `jsonschema`), SPDX license, README, tests
  - No CLI/daemon or built-in collectors
- Main repo: `dwellir-harvester`
  - Depends on `dwellir-harvester-lib`
  - Keeps CLI/daemon, built-in collectors, docs/examples

## Steps
1) Identify core code to move
   - Move `collector_base.py`, core types (`CollectResult`, metadata/errors), loader helpers (`load_collectors` and helpers), schema helpers, `lib.run` runner into the new repo under `src/dwellir_harvester/lib/…`
   - Ensure imports avoid CLI/daemon/built-ins

2) Create `dwellir-harvester-lib` repo/package
   - Init repo with `pyproject.toml` (`name = "dwellir-harvester-lib"`, `package-dir = {"": "src"}`, minimal deps, SPDX license)
   - Add README and tests (import tests, plugin loader tests)
   - Copy relevant code/tests; adjust imports to the lib namespace

3) Publish / dev installs
   - For local/dev: install via VCS URL (e.g., `pip install git+https://github.com/<you>/dwellir-harvester-lib.git@branch`)
   - For release: publish to PyPI when ready

4) Update main repo
   - Add `dwellir-harvester-lib` as a dependency in `pyproject.toml`
   - Update imports in CLI/daemon/built-ins to use `dwellir_harvester.lib`
   - Remove duplicated core code or keep shims during transition; delegate loader to the lib implementation

5) Docs and examples
   - In `dwellir-harvester-lib`: document SDK (collector bases, return contract, plugin paths, runner)
   - In `dwellir-harvester`: document dependency on the lib, plugin flags/env, how to point to local collectors

6) Testing/CI
   - Set up CI in the lib repo (imports, plugin loader tests)
   - Update main repo CI to install the lib (PyPI or VCS) and run the suite

7) Migration
   - Tag/release `dwellir-harvester-lib`
   - Update main package dependency/version; release main package after verification

## Notes
- Keep the lib minimal (no CLI/daemon/build-in collectors) to remain stable for charm/plugin authors
- Collision policy/order in loader remains as implemented (built-ins → entry points → filesystem, warn-and-override) in the lib
