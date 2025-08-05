from dataclasses import dataclass


@dataclass
class ContactFormDto:
    id: str
    title: str
    csv_file_path: str
