import csv
import sys
from types import TracebackType
from typing import Any, Self, TextIO

from review.writer import AbstractReviewWriter
from review import Review


class ReviewCsvWriter(AbstractReviewWriter):
    _f: TextIO
    _file_path: str
    _is_closed: bool = True

    @staticmethod
    def _get_header_fields() -> list[str]:
        return [
            "hotel_name",
            "review_text",
            "rating",
            "review_timestamp",
            "trip_type",
            "trip_companions",
        ]

    @staticmethod
    def _get_writable_row(review: Review) -> list[Any]:
        timestamp: str = (
            review.review_timestamp.strftime("%Y-%m-%d")
            if review.review_timestamp is not None
            else ""
        )

        return [
            review.hotel_name,
            review.review_text.replace("\n", ""),
            round(review.rating, 1),
            timestamp,
            review.trip_type,
            review.trip_companions,
        ]

    def __init__(self, file_path: str | None = None) -> None:
        if file_path is not None:
            self._f = open(file_path, "w", newline="", encoding="utf-8")
            self._file_path = file_path
        else:
            self._f = sys.stdout
            self._file_path = "sys.stdout"
        self._is_closed = False
        self._writer = csv.writer(self._f, quoting=csv.QUOTE_NONNUMERIC)
        self._writer.writerow(self._get_header_fields())

    def __enter__(self) -> Self:
        return self

    def _warn_closed(self) -> None:
        print(
            f"[CsvReviewWriter] Warning: File {self._file_path} is closed",
            file=sys.stderr,
        )

    def append(self, reviews: list[Review]) -> None:
        if self._is_closed:
            self._warn_closed()
            return
        self._writer.writerows(
            self._get_writable_row(review) for review in reviews
        )

    def close(self) -> None:
        if not self._is_closed:
            self._f.close()
            self._is_closed = True
        else:
            self._warn_closed()

    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        self.close()
