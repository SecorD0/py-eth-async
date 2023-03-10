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
    pass
