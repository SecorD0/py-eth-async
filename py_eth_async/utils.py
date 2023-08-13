from typing import Union, Optional, Dict, Any

import aiohttp
from eth_typing import ChecksumAddress
from eth_utils import to_checksum_address

from py_eth_async import exceptions


def api_key_required(func):
    """Check if the Blockscan API key is specified."""

    def func_wrapper(self, *args, **kwargs):
        if not self.client.network.api.key or not self.client.network.api.functions:
            raise exceptions.APIException('To use this function, you must specify the explorer API key!')

        else:
            return func(self, *args, **kwargs)

    return func_wrapper


def checksum(address: str) -> ChecksumAddress:
    """
    Convert an address to checksummed.

    Args:
        address (str): the address.

    Returns:
        ChecksumAddress: the checksummed address.

    """
    return to_checksum_address(address)


def aiohttp_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Union[str, int, float]]]:
    """
    Convert requests params to aiohttp params.

    Args:
        params (Optional[Dict[str, Any]]): requests params.

    Returns:
        Optional[Dict[str, Union[str, int, float]]]: aiohttp params.

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
    Make a GET request and check if it was successful.

    Args:
        url (str): a URL.
        headers (Optional[dict]): the headers. (None)
        **kwargs: arguments for a GET request, e.g. 'params', 'headers', 'data' or 'json'.

    Returns:
        Optional[dict]: received dictionary in response.

    """
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url=url, **kwargs) as response:
            status_code = response.status
            response = await response.json()
            if status_code <= 201:
                return response

            raise exceptions.HTTPException(response=response, status_code=status_code)


async def get_coin_symbol(chain_id: Union[int, str]) -> str:
    """
    Get a coin symbol on a network with the specified ID.

    Args:
        chain_id (Union[int, str]): the network ID.

    Returns:
        str: the coin symbol.

    """
    response = await async_get('https://chainid.network/chains.json')
    network = next((network for network in response if network['chainId'] == int(chain_id)), None)
    if network:
        return network['nativeCurrency']['symbol']

    return ''
