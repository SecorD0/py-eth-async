from typing import Optional, Union

from eth_typing import Address

from py_eth_async.data import types
from py_eth_async.data.models import Wei, TokenAmount
from py_eth_async.utils import checksum


class Wallet:
    def __init__(self, client) -> None:
        """
        Initialize a class with functions related to wallet.

        :param Client client: the Client instance
        """
        self.client = client

    async def balance(self, token: Optional[types.Contract] = None,
                      address: Optional[types.Address] = None) -> Union[Wei, TokenAmount]:
        """
        Get a coin or token balance of a specified address.

        :param Optional[Contract] token: the contact address or instance of token (coin)
        :param Optional[Address] address: the address (imported to client address)
        :return Union[Wei, TokenAmount]: the coin or token balance
        """
        if not address:
            address = self.client.account.address

        address = checksum(address)
        if not token:
            return Wei(await self.client.w3.eth.get_balance(account=address))

        contract_address, abi = await self.client.contracts.get_contract_attributes(token)
        contract = await self.client.contracts.default_token(contract_address=contract_address)
        return TokenAmount(amount=await contract.functions.balanceOf(address).call(),
                           decimals=await contract.functions.decimals().call(), wei=True)

    async def nonce(self, address: Optional[types.Contract] = None) -> int:
        """
        Get a nonce of the specified address.

        :param Optional[Contract] address: the address (imported to client address)
        :return int: the nonce of the address
        """
        if not address:
            address = self.client.account.address

        else:
            address, abi = await self.client.contracts.get_contract_attributes(address)

        return await self.client.w3.eth.get_transaction_count(address)
