# Juju Charm Collector — Implementation Plan

## Goal
Create a generic collector that runs inside a Juju charm context and returns charm configuration/state as JSON to include in the harvester output. It should gracefully degrade or provide a mockable path when run outside a Juju context for local testing.

## Output Shape (draft)
```json
{
  "juju_charm": {
    "application": "my-charm",
    "unit": "my-charm/0",
    "model": "my-model",
    "controller": "my-controller",
    "config": { "key": "value", "...": "..." },
    "relations": [
      {
        "name": "db",
        "interface": "postgresql",
        "endpoints": ["my-charm:db", "postgresql/0:db"]
      }
    ],
    "status": {
      "app": "active",
      "unit": "active"
    },
    "notes": null
  }
}
```

## Approach
1. **Collector**: Implement `JujuCharmCollector` as a `GenericCollector` relying on the `ops` library (Charmcraft’s Operator Framework) to read charm metadata, config, and relation data.
2. **Ops dependency**: Add an optional dependency `ops` (or document that the collector requires it). Fail with a clear error if missing.
3. **Context detection**: Detect if running in a Juju charm context (e.g., env vars like `JUJU_CHARM_DIR`, `JUJU_MODEL_NAME`, presence of hook tools or `OPS_*`). If not present, return a placeholder with `notes` indicating “not running inside Juju charm context”.
4. **Data gathering (inside charm)**:
   - Application and unit names, model, controller if available.
   - Config: `model.config` or `ops.model.config`.
   - Relations summary: relation names, interface, endpoints (omit relation data payload by default to avoid secrets).
   - Status: application/unit status strings.
5. **Secrets handling**: Avoid emitting relation data or any secret values; keep to metadata/config only.
6. **Testing strategy**:
   - Local/non-Juju: ensure collector returns a structured placeholder with `notes`.
   - Charm-harness tests: use `ops.testing.Harness` to simulate config and relations and assert output shape.
   - Manual: run via a Juju action inside a deployed charm and inspect JSON.
7. **Integration**:
   - Register collector in `collectors/__init__.py`.
   - Document usage in README (requires running inside a charm; otherwise placeholder).
   - Optionally add a CLI flag or environment variable to allow a mock JSON file for offline testing.

## Steps
1) Add optional dependency `ops` (or document requirement) in `pyproject.toml` under an extra (e.g., `juju`) if preferred.
2) Implement `JujuCharmCollector` in `collectors/juju_charm.py`:
   - Detect context; if absent, return placeholder with `notes`.
   - When present, use `ops` to read config, relations (metadata only), status, names.
   - Scrub secrets and keep payload minimal.
3) Add tests:
   - Unit test outside Juju: expect placeholder.
   - Harness-based test to validate populated fields with fake config/relations.
4) Register collector and update README with usage and limitations.
5) Provide example Juju action snippet to run harvester and inspect JSON.
