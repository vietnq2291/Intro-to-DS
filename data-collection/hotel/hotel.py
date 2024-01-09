from dataclasses import dataclass


@dataclass
class Hotel:
    # The site from which data are collected
    source: str
    name: str
    address: str
    images_count: int
    popular_amenities: list[str]
