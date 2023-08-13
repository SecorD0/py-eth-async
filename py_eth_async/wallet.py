from typing import Optional, Union

from eth_typing import Address

from py_eth_async.data import types
from py_eth_async.data.models import Wei, TokenAmount
from py_eth_async.utils import checksum


class Wallet:
    """
    Class with functions related to wallet.

    Attributes:
        client (Client): the Client instance.

    """

    def __init__(self, client) -> None:
        """
        Initialize the class.

        Args:
            client (Client): the Client instance.

        """
        self.client = client

    async def balance(
            self, token: Optional[types.Contract] = None, address: Optional[types.Address] = None
    ) -> Union[Wei, TokenAmount]:
        """
        Get a coin or token balance of a specified address.

        Args:
            token (Optional[Contract]): the contact address or instance of token. (coin)
            address (Optional[Address]): the address. (imported to client address)

        Returns:
            Union[Wei, TokenAmount]: the coin or token balance.

        """
        if not address:
            address = self.client.account.address

        address = checksum(address)
        if not token:
            return Wei(await self.client.w3.eth.get_balance(account=address))

        contract_address, abi = await self.client.contracts.get_contract_attributes(token)
        contract = await self.client.contracts.default_token(contract_address=contract_address)
        return TokenAmount(
            amount=await contract.functions.balanceOf(address).call(),
            decimals=await contract.functions.decimals().call(), wei=True
        )

    async def nonce(self, address: Optional[types.Contract] = None) -> int:
        """
        Get a nonce of the specified address.

        Args:
            address (Optional[Contract]): the address. (imported to client address)

        Returns:
            int: the nonce of the address.

        """
        if not address:
            address = self.client.account.address

        else:
            address, abi = await self.client.contracts.get_contract_attributes(address)

        return await self.client.w3.eth.get_transaction_count(address)
