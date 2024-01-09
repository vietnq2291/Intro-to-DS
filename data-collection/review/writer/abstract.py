from abc import ABC, abstractmethod

from review import Review


class AbstractReviewWriter(ABC):
    @abstractmethod
    def append(self, reviews: list[Review]) -> None:
        pass
