from dataclasses import dataclass


@dataclass
class PageDto:
    ID: int
    post_title: str
    post_name: str
    post_date: str
    post_status: str
