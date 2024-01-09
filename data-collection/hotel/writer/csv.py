import csv
import sys
from types import TracebackType
from typing import Self, TextIO
from hotel import Hotel
from hotel.writer import AbstractHotelWriter


class HotelCsvWriter(AbstractHotelWriter):
    _f: TextIO
    _file_path: str
    _is_closed: bool = True

    @staticmethod
    def _get_header_fields() -> list[str]:
        return [
            "name",
            "address",
            "images_count",
            "popular_amenities",
            "source",
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

    def append(self, hotel: Hotel) -> None:
        if self._is_closed:
            self._warn_closed()
            return
        self._writer.writerow(
            [
                hotel.name,
                hotel.address,
                hotel.images_count,
                hotel.popular_amenities,
                hotel.source,
            ]
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
