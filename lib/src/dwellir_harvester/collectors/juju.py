import json
import logging
import socket
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from ..collector_base import CollectResult, GenericCollector, CollectorError

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class JujuCollector(GenericCollector):
    """Collector for local Juju agent topology (single machine)."""

    NAME = "juju"
    VERSION = "0.1.0"
    AGENTS_DIR = Path("/var/lib/juju/agents")
    SECRET_KEYS = {"apipassword", "oldpassword", "password"}

    @classmethod
    def create(cls, *args, **kwargs) -> 'JujuCollector':
        """Factory method to create a new instance."""
        return cls(*args, **kwargs)

    def _read_yaml(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load a YAML file safely."""
        try:
            import yaml  # type: ignore
        except Exception as e:  # pragma: no cover - dependency issue
            raise CollectorError(f"PyYAML is required to parse {path}") from e

        try:
            with path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.debug("agent.conf not found at %s", path)
        except Exception as e:
            logger.warning("Failed to parse %s: %s", path, e)
        return None

    def _scrub(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove secret-like keys from a parsed agent.conf."""
        cleaned = {}
        for k, v in data.items():
            if k in self.SECRET_KEYS:
                continue
            # Drop big certs by default
            if k == "cacert":
                continue
            cleaned[k] = v
        return cleaned

    def _split_units(self, values: Dict[str, Any]) -> List[str]:
        units_raw = values.get("deployed-units")
        if not units_raw:
            return []
        return [u.strip() for u in str(units_raw).split(",") if u.strip()]

    def _load_machine(self) -> Optional[Dict[str, Any]]:
        if not self.AGENTS_DIR.exists():
            logger.info("Juju agents directory not found: %s", self.AGENTS_DIR)
            return None
        machine_dirs = sorted([p for p in self.AGENTS_DIR.glob("machine-*") if p.is_dir()])
        if not machine_dirs:
            logger.info("No Juju machine agents found under %s", self.AGENTS_DIR)
            return None
        conf_path = machine_dirs[0] / "agent.conf"
        data = self._read_yaml(conf_path)
        if not data:
            return None
        return self._scrub(data)

    def _load_units(self) -> List[Dict[str, Any]]:
        """Load unit agent configs."""
        if not self.AGENTS_DIR.exists():
            return []
        units: List[Dict[str, Any]] = []
        for path in sorted(self.AGENTS_DIR.glob("unit-*")):
            if not path.is_dir():
                continue
            conf = self._read_yaml(path / "agent.conf")
            if not conf:
                continue
            conf = self._scrub(conf)
            units.append(conf)
        return units

    def collect(self) -> Dict[str, Any]:
        hostname = socket.gethostname()
        machine_conf = self._load_machine()
        unit_confs = self._load_units()

        juju_data: Dict[str, Any] = {
            "controller": None,
            "model": None,
            "tag": None,
            "instance_id": None,  # not implemented
            "dns_name": hostname,
            "hostname": hostname,
            "version": None,
            "units_deployed": [],
            "units": [],
        }

        if machine_conf:
            juju_data["controller"] = machine_conf.get("controller")
            juju_data["model"] = machine_conf.get("model")
            juju_data["tag"] = machine_conf.get("tag")
            juju_data["version"] = machine_conf.get("upgradedToVersion")
            values = machine_conf.get("values", {}) if isinstance(machine_conf.get("values"), dict) else {}
            juju_data["units_deployed"] = self._split_units(values)

        for uconf in unit_confs:
            unit_entry = {
                "tag": uconf.get("tag"),
                "controller": uconf.get("controller"),
                "model": uconf.get("model"),
                "notes": None,
            }
            juju_data["units"].append(unit_entry)

        # If nothing found, add a note
        if not machine_conf and not unit_confs:
            juju_data["notes"] = "No Juju agents found under /var/lib/juju/agents"

        return CollectResult.create(
            collector_name=self.NAME,
            collector_version=self.VERSION,
            data={"juju": juju_data},
        )
