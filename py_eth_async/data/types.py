from typing import Union

from web3 import Web3, types
from web3.contract import AsyncContract

from .models import RawContract, TokenAmount, Ether, Wei, GWei

Address = Union[str, types.Address, types.ChecksumAddress, types.ENS]
Amount = Union[float, int, TokenAmount, Ether, Wei]
Contract = Union[str, types.Address, types.ChecksumAddress, types.ENS, RawContract, AsyncContract]
GasLimit = Union[int, Wei]
GasPrice = Union[float, int, Wei, GWei]
Web3Async = Web3
