from __future__ import annotations
from ..core import BaseCollector, CollectResult
from ._substrate_common import collect_substrate


class AjunaCollector(BaseCollector):
    NAME = "ajuna"
    VERSION = "0.1.0"

    def collect(self) -> CollectResult:
        return collect_substrate(self.NAME)
