from __future__ import annotations
from ..core import BaseCollector, CollectResult
from ._substrate_common import collect_substrate, SUBSTRATE_COLLECTOR_VERSION


class PolkadotCollector(BaseCollector):
    NAME = "polkadot"
    VERSION = SUBSTRATE_COLLECTOR_VERSION

    def collect(self) -> CollectResult:
        return collect_substrate(self.NAME)
