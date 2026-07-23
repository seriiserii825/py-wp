from dataclasses import dataclass


@dataclass
class TermDto:
    term_id: int
    name: str
    slug: str
