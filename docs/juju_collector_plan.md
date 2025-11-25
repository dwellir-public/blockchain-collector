# Juju Collector — Implementation Plan

## Goal
Implement a `juju` collector that discovers Juju agents on the local machine, reads their `agent.conf` files under `/var/lib/juju/agents/`, and emits a JSON structure describing the machine and its units (topology) without exposing secrets.

## Discovery
- Base path: `/var/lib/juju/agents/`
- Machine agent dirs: `machine-*` with `agent.conf`
- Unit agent dirs: `unit-*-*` with `agent.conf`
- Ignore entries without `agent.conf`

## Data extraction
- Parse `agent.conf` (YAML) per agent.
- Machine agent fields of interest:
  - `tag` (e.g., `machine-0`)
  - `upgradedToVersion`
  - `controller`
  - `model`
  - `values` (for deployed units list, service names)
  - Paths (datadir, logdir) for context (non-secret)
- Unit agent fields of interest:
  - `tag` (e.g., `unit-tiny-bash-0`)
  - `controller`
  - `model`
  - `upgradedToVersion`
- Treat sensitive fields as secrets, do not emit:
  - `apipassword`, `oldpassword`, any fields named `password` or secrets; trim CA cert bodies unless explicitly wanted (likely omit).

## Proposed JSON structure (draft)
```json
{
  "juju": {
    "controller": "controller-58898865-d278-4bdc-8c95-c903c077eae3",
    "model": "model-cf018491-7a10-4f69-8ac6-b2125255b1db",
    "instance_id": "",
    "tag": "machine-0",
    "dns_name": "hostname.example.local",
    "hostname": "hostname.example.local",
    "version": "3.6.11",
    "units_deployed": ["tiny-bash/0", "ubuntu/0"],
    "units": [
      {
        "tag": "unit-tiny-bash-0",
        "controller": "controller-58898865-d278-4bdc-8c95-c903c077eae3",
        "model": "model-cf018491-7a10-4f69-8ac6-b2125255b1db",
        "notes": null
      }
    ]
  }
}
```

Notes:
- `units_deployed` only on machine (from `values.deployed-units` if present); units do not carry this.
- Single-machine scope (local host only); no multi-machine array needed.
- `tag` comes from machine agent tag; `instance_id` left empty/null (not implemented yet); `dns_name` uses local hostname by default.
- Keep structure lean: omit `jobs`, service name, dirs, api addresses, raw `values`, and per-unit version/units_deployed.
- Do not emit `apipassword`, `oldpassword`, full CA certs, or other secrets.

## Steps
1) Add `juju.py` collector (likely subclass `CollectorBase` or `GenericCollector` depending on schema needs).
2) Implement discovery of agents under `/var/lib/juju/agents/` with filesystem guards.
3) Parse `agent.conf` via `yaml.safe_load`, handle errors gracefully; skip unreadable/invalid files with warnings.
4) Scrub secrets (`password`, `apipassword`, `oldpassword`, etc.); optionally keep hashes/flags only.
5) Build the JSON structure above; tolerate missing fields.
6) Add tests with fixture agent.conf files (machine + unit) to validate parsing and shape.
7) Add README entry describing the juju collector and output fields.
8) Add to `__all__`/collector registration.
