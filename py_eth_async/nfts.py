import json
from typing import Union
from urllib.request import urlopen

from eth_typing import Address, ChecksumAddress
from web3.contract import AsyncContract
from web3.types import ENS

from py_eth_async import exceptions
from py_eth_async.data.models import NFT
from py_eth_async.utils import async_get


class NFTs:
    def __init__(self, client) -> None:
        """
        Initialize a class with functions related to NTFs.

        :param Client client: the Client instance
        """
        self.client = client

    async def get_info(self, contract: Union[str, Address, ChecksumAddress, ENS, AsyncContract],
                       token_id: Union[int, str] = None) -> NFT:
        """
        Get information about a NFT.

        :param Union[str, Address, ChecksumAddress, ENS, AsyncContract] contract: the contract address or instance of a NFT collection
        :param Union[int, str] token_id: the NFT ID to parse the owner and attributes (None)
        :return NFT: the NFT
        """
        contract_address = contract.address if isinstance(contract, AsyncContract) else contract
        contract = await self.client.contracts.default_nft(contract_address)
        nft = NFT(contract_address=contract_address)
        nft.name = await contract.functions.name().call()
        nft.symbol = await contract.functions.symbol().call()
        nft.total_supply = await contract.functions.totalSupply().call()
        if token_id:
            try:
                token_id = int(token_id)
                if token_id >= nft.total_supply:
                    exceptions.NFTException('The token ID exceeds total supply!')

                nft.id = token_id
                try:
                    nft.owner = await contract.functions.ownerOf(token_id).call()
                except:
                    pass

                image_url = await contract.functions.tokenURI(token_id).call()
                if 'data:application/json' in image_url:
                    with urlopen(image_url) as response:
                        response = json.loads(response.read())

                else:
                    if 'ipfs://' in image_url:
                        image_url = image_url.replace('ipfs://', 'https://ipfs.io/ipfs/')

                    nft.image_url = image_url
                    response = await async_get(image_url)

                if 'attributes' in response and response['attributes']:
                    nft.parse_attributes(response['attributes'])

            except:
                pass

        return nft
