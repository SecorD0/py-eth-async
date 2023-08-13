from typing import Optional, Dict, Any


class ClientException(Exception):
    pass


class InvalidProxy(ClientException):
    pass


class APIException(Exception):
    pass


class ContractException(Exception):
    pass


class NFTException(Exception):
    pass


class TransactionException(Exception):
    pass


class NoSuchToken(TransactionException):
    pass


class InsufficientBalance(TransactionException):
    pass


class GasPriceTooHigh(TransactionException):
    pass


class FailedToApprove(TransactionException):
    pass


class WalletException(Exception):
    pass


class HTTPException(Exception):
    """
    An exception that occurs when an HTTP request is unsuccessful.

    Attributes:
        response (Optional[Dict[str, Any]]): a JSON response to a request.
        status_code (Optional[int]): a request status code.

    """
    response: Optional[Dict[str, Any]]
    status_code: Optional[int]

    def __init__(self, response: Optional[Dict[str, Any]] = None, status_code: Optional[int] = None) -> None:
        """
        Initialize the class.

        Args:
            response (Optional[Dict[str, Any]]): a JSON response to a request. (None)
            status_code (Optional[int]): a request status code. (None)

        """
        self.response = response
        self.status_code = status_code

    def __str__(self):
        if self.response:
            return f'{self.status_code}: {self.response}'

        return f'{self.status_code}'
