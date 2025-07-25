from dataclasses import dataclass


@dataclass
class CsvPluginDto:
    plugin_slug: str
    filename: str
