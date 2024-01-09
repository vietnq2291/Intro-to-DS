from dataclasses import dataclass
import datetime


@dataclass
class Review:
    hotel_name: str = ""
    review_text: str = ""
    rating: float = 0.0
    review_timestamp: datetime.datetime | None = None
    trip_type: str | None = None
    trip_companions: str | None = None
