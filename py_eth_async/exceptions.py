from typing import Optional


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
    def __init__(self, response: Optional[dict] = None, status_code: Optional[int] = None) -> None:
        self.response = response
        self.status_code = status_code

    def __str__(self):
        if self.response:
            return f'{self.status_code}: {self.response}'

        return f'{self.status_code}'
