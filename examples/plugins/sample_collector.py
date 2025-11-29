from dwellir_harvester.collector_base import GenericCollector


class SamplePluginCollector(GenericCollector):
    NAME = "sample_plugin"
    VERSION = "0.0.1"

    def collect(self):
        return {"metadata": self._get_metadata(), "data": {"message": "hello from plugin"}}

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)
