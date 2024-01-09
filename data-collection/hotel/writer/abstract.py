from abc import ABC, abstractmethod

from hotel.hotel import Hotel


class AbstractHotelWriter(ABC):
    @abstractmethod
    def append(self, hotel: Hotel) -> None:
        pass
