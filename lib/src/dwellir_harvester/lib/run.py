"""Simple runner to execute a collector class directly (for SDK/testing)."""

import argparse
import importlib
import json
import sys
from typing import Any, Optional

from . import CollectorBase


def _load_class(dotted: str):
    if ":" in dotted:
        module_name, cls_name = dotted.split(":", 1)
    elif "." in dotted:
        parts = dotted.split(".")
        module_name, cls_name = ".".join(parts[:-1]), parts[-1]
    else:
        raise ValueError("Collector must be specified as module:Class or module.Class")
    mod = importlib.import_module(module_name)
    cls = getattr(mod, cls_name, None)
    if cls is None:
        raise ImportError(f"Class {cls_name} not found in module {module_name}")
    return cls


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run a dwellir-harvester collector class directly.")
    parser.add_argument("collector", help="Collector class (module:Class or module.Class)")
    parser.add_argument(
        "--collector-path",
        action="append",
        dest="collector_paths",
        default=[],
        help="Additional paths to add to sys.path when importing the collector.",
    )
    args = parser.parse_args(argv)

    for p in args.collector_paths:
        if p not in sys.path:
            sys.path.insert(0, p)

    try:
        cls = _load_class(args.collector)
        if not issubclass(cls, CollectorBase):
            raise TypeError(f"{cls} is not a CollectorBase subclass")
        if hasattr(cls, "create"):
            inst = cls.create()
        else:
            inst = cls()
        result = inst.run()
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(f"Error running collector: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
