from typing import Union, Optional, Dict, Any

import aiohttp
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address

from py_eth_async import exceptions


def api_key_required(func):
    """Check if the explorer API key is specified."""

    def func_wrapper(self, *args, **kwargs):
        if not self.client.network.api.key:
            raise exceptions.APIException('To use this function, you must specify the explorer API key!')

        else:
            return func(self, *args, **kwargs)

    return func_wrapper


def checksum(address: str) -> ChecksumAddress:
    """
    Convert an address to checksummed.

    :param str address: the address
    :return ChecksumAddress: the checksummed address
    """
    return to_checksum_address(address)


def aiohttp_params(params: Union[Dict[str, Any], None]) -> Union[Dict[str, Union[str, int, float]], None]:
    """
    Convert requests params to aiohttp params.

    :param Union[Dict[str, Any], None] params: requests params
    :return Union[Dict[str, Union[str, int, float]], None]: aiohttp params
    """
    new_params = params.copy()
    if not params:
        return

    for key, value in params.items():
        if value is None:
            del new_params[key]

        if isinstance(value, bool):
            new_params[key] = str(value).lower()

    return new_params


async def async_get(url: str, headers: Optional[dict] = None, **kwargs) -> Optional[dict]:
    """
    Make asynchronous GET request.

    :param str url: a URL
    :param Optional[dict] headers: headers (None)
    :param kwargs: arguments for a GET request, e.g. 'params', 'data' or 'json'
    :return Optional[dict]: received dictionary in response
    """
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url=url, **kwargs) as response:
            if response.status <= 201:
                return await response.json()

            raise exceptions.HTTPException()


async def get_coin_symbol(chain_id: Union[int, str]) -> str:
    """
    Get a coin symbol on a network with the specified ID.

    :param Union[int, str] chain_id: the network ID
    :return str: the coin symbol
    """
    response = await async_get('https://chainid.network/chains.json')
    network = next((network for network in response if network['chainId'] == int(chain_id)), None)
    if network:
        return network['nativeCurrency']['symbol']

    return ''
