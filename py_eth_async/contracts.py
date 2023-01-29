import asyncio
import json
from typing import Union, Optional, List, Dict, Any

from evmdasm import EvmBytecode
from pretty_utils.type_functions.strings import text_between
from web3.contract import AsyncContract

from py_eth_async.data import types
from py_eth_async.data.models import DefaultABIs, ABI, Function, RawContract
from py_eth_async.utils import checksum, async_get


class Contracts:
    def __init__(self, client) -> None:
        """
        Initialize a class with functions related to contracts.

        :param Client client: the Client instance
        """
        self.client = client

    @staticmethod
    async def get_signature(hex_signature: str) -> Optional[list]:
        """
        Find all matching signatures in the database of https://www.4byte.directory/.

        :param str hex_signature: a signature hash
        :return Optional[list]: matches found
        """
        try:
            response = await async_get(f'https://www.4byte.directory/api/v1/signatures/?hex_signature={hex_signature}')
            results = response['results']
            return [m['text_signature'] for m in sorted(results, key=lambda result: result['created_at'])]

        except:
            return

    @staticmethod
    async def parse_function(text_signature: str) -> dict:
        """
        Construct a function dictionary for the Application Binary Interface (ABI) based on the provided text signature.

        :param str text_signature: a text signature, e.g. approve(address,uint256)
        :return dict: the function dictionary for the ABI
        """
        name, sign = text_signature.split('(', 1)
        sign = sign[:-1]
        tuples = []
        while '(' in sign:
            tuple_ = text_between(text=sign[:-1], begin='(', end=')')
            tuples.append(tuple_.split(',') or [])
            sign = sign.replace(f'({tuple_})', 'tuple')

        inputs = sign.split(',')
        if inputs == ['']:
            inputs = []

        function = {
            'type': 'function',
            'name': name,
            'inputs': [],
            'outputs': [{'type': 'uint256'}]
        }
        i = 0
        for type_ in inputs:
            input_ = {'type': type_}
            if type_ == 'tuple':
                input_['components'] = [{'type': comp_type} for comp_type in tuples[i]]
                i += 1

            function['inputs'].append(input_)

        return function

    async def get_abi(self, contract_address: types.Contract,
                      raw_json: bool = False) -> Union[str, List[Dict[str, Any]]]:
        """
        Get a contract ABI from the Etherscan API, if unsuccessful, parses it based on the contract source code (it may be incorrect or incomplete).

        :param Contract contract_address: the contract address
        :param bool raw_json: if True, it returns serialize string, otherwise it returns Python list (False)
        :return Union[str, List[Dict[str, Any]]]: the ABI
        """
        if isinstance(contract_address, AsyncContract) or isinstance(contract_address, RawContract):
            contract_address = contract_address.address

        else:
            contract_address = checksum(contract_address)

        abi = []
        if self.client.network.api.key:
            try:
                abi = (await self.client.network.api.functions.contract.getabi(contract_address))['result']
                abi = json.loads(abi)

            except:
                abi = []

        if not abi:
            bytecode = await self.client.w3.eth.get_code(contract_address)
            opcodes = EvmBytecode(bytecode).disassemble()
            hex_signatures = set()
            for i in range(len(opcodes) - 3):
                if (
                        opcodes[i].name == 'PUSH4'
                        and opcodes[i + 1].name == 'EQ'
                        and opcodes[i + 2].name == 'PUSH2'
                        and opcodes[i + 3].name == 'JUMPI'
                ):
                    hex_signatures.add(opcodes[i].operand)
            hex_signatures = list(hex_signatures)

            text_signatures = []
            for i, hex_signature in enumerate(hex_signatures):
                signature_for_hash = await Contracts.get_signature(hex_signature=hex_signature)
                while signature_for_hash is None:
                    await asyncio.sleep(1)
                    signature_for_hash = await Contracts.get_signature(hex_signature=hex_signature)

                if signature_for_hash:
                    text_signatures.append(signature_for_hash[0])

            for text_signature in text_signatures:
                try:
                    abi.append(await Contracts.parse_function(text_signature=text_signature))

                except:
                    pass

        if raw_json:
            return json.dumps(abi)

        return abi

    async def default_token(self, contract_address: types.Contract) -> AsyncContract:
        """
        Get a token contract instance with a standard set of functions.

        :param Contract contract_address: the contract address
        :return AsyncContract: the token contract instance
        """
        if isinstance(contract_address, AsyncContract) or isinstance(contract_address, RawContract):
            contract_address = contract_address.address

        else:
            contract_address = checksum(contract_address)

        return self.client.w3.eth.contract(address=contract_address, abi=DefaultABIs.Token)

    async def default_nft(self, contract_address: types.Contract) -> AsyncContract:
        """
        Get a NFT contract instance with a standard set of functions.

        :param Contract contract_address: the contract address
        :return AsyncContract: the NFT contract instance
        """
        if isinstance(contract_address, AsyncContract) or isinstance(contract_address, RawContract):
            contract_address = contract_address.address

        else:
            contract_address = checksum(contract_address)

        return self.client.w3.eth.contract(address=contract_address, abi=DefaultABIs.NFT)

    async def get(self, contract_address: types.Contract, abi: Optional[Union[list, str]] = None,
                  proxy_address: Optional[types.Contract] = None) -> AsyncContract:
        """
        Get a contract instance.

        :param Contract contract_address: the contract address
        :param Optional[Union[list, str]] abi: the contract ABI (get it using the 'get_abi' function)
        :param Optional[Contract] proxy_address: the contract proxy address (None)
        :return AsyncContract: the contract instance
        """
        if isinstance(contract_address, AsyncContract) or isinstance(contract_address, RawContract):
            contract_address = contract_address.address

        else:
            contract_address = checksum(contract_address)

        if not abi:
            if proxy_address:
                if isinstance(proxy_address, AsyncContract) or isinstance(proxy_address, RawContract):
                    abi_contract = proxy_address.address

                else:
                    abi_contract = checksum(proxy_address)

            else:
                abi_contract = contract_address

            abi = await self.get_abi(contract_address=abi_contract)

        if abi:
            return self.client.w3.eth.contract(address=contract_address, abi=abi)

        return self.client.w3.eth.contract(address=contract_address)

    async def get_functions(self, contract: types.Contract) -> List[Function]:
        """
        Get functions of a contract in human-readable form.

        :param Contract contract: the contract address or instance
        :return List[Function]: functions of the contract
        """
        if isinstance(contract, RawContract):
            contract = await self.get(contract_address=contract.address)

        elif not isinstance(contract, AsyncContract):
            contract = await self.get(contract_address=checksum(contract))

        abi = contract.abi or []
        return ABI(abi=abi).functions
