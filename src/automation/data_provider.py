from abc import ABC, abstractmethod
from typing import Dict, Any, List

class DataProvider(ABC):
    """
    Abstract Base Class for defining the interface for all IRCTC data providers.
    """

    @abstractmethod
    def login(self, username, password, captcha_callback) -> bool:
        """
        Handles the login process.
        Returns True on success, False on failure.
        """
        pass

    @abstractmethod
    def plan_journey(self, from_station: str, to_station: str, date_str: str):
        """
        Fills out the journey planning form and initiates a search for trains.
        """
        pass

    @abstractmethod
    def get_trains(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parses and returns a list of available trains after a search.
        The filters can be used to narrow down the results.
        """
        pass

    @abstractmethod
    def book_ticket(self, train: Dict[str, Any], passengers: List[Dict[str, Any]], payment_callback) -> Dict[str, str]:
        """
        Handles the entire booking process for a selected train.
        This includes filling passenger details and handling payment.
        Returns a dictionary with the PNR and booking status.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Cleans up and closes any resources used by the provider (e.g., browser).
        """
        pass
