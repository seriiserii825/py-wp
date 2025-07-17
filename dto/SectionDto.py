from dataclasses import dataclass


@dataclass
class SectionDTO():
    ID: int
    post_title: str
    post_name: str
    post_date: str
    post_status: str
