from typing import Union, Optional, Dict, Any

import aiohttp
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address

from py_eth_async import exceptions


def api_key_required(func):
    """Check if the explorer API key is specified."""

    def func_wrapper(self, *args, **kwargs):
        if not self.client.network.api.key or not self.client.network.api.functions:
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


def aiohttp_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Union[str, int, float]]]:
    """
    Convert requests params to aiohttp params.

    :param Optional[Dict[str, Any]] params: requests params
    :return Optional[Dict[str, Union[str, int, float]]]: aiohttp params
    """
    print("This function will be deprecated in the next major update. "
          "Use the 'aiohttp_params' function from the 'pretty-utils' library.")
    new_params = params.copy()
    if not params:
        return

    for key, value in params.items():
        if value is None:
            del new_params[key]

        if isinstance(value, bool):
            new_params[key] = str(value).lower()

        elif isinstance(value, bytes):
            new_params[key] = value.decode('utf-8')

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
            status_code = response.status
            response = await response.json()
            if status_code <= 201:
                status = response.get('status')
                if status is not None and not int(status):
                    raise exceptions.HTTPException(response=response, status_code=status_code)

                return response

            raise exceptions.HTTPException(response=response, status_code=status_code)


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
