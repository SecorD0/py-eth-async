from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Union, Dict, List, Any, Tuple

import requests
from eth_typing import ChecksumAddress
from eth_utils import to_wei, from_wei
from pretty_utils.type_functions.classes import AutoRepr
from web3 import Web3

from py_eth_async import config
from py_eth_async.blockscan_api import APIFunctions
from py_eth_async.utils import checksum


@dataclass
class API:
    """
    An instance that contains an API related information.

    Attributes:
        key (str): an API-key.
        url (str): an API entrypoint URL.
        docs (str): a docs URL.
        functions (Optional[APIFunctions]): the functions instance.

    """
    key: str
    url: str
    docs: str
    functions: Optional[APIFunctions] = None


class DEX:
    """
    An instance that contains a DEX related information.

    Attributes:
        name (str): a DEX name.
        factory (Optional[ChecksumAddress]): a factory contract address.
        router (Optional[ChecksumAddress]): a router contract address.

    """
    name: str
    factory: Optional[ChecksumAddress]
    router: Optional[ChecksumAddress]

    def __init__(self, name: str, factory: Optional[str] = None, router: Optional[str] = None) -> None:
        self.name = name
        self.factory = checksum(factory) if factory else None
        self.router = checksum(router) if router else None


class Network(AutoRepr):
    """
    An instance of a network that is used in the Client.

    Attributes:
        name (str): a network name.
        rpc (str): the RPC URL.
        chain_id (Optional[int]): the chain ID.
        tx_type (int): the main type of transactions in the network. Either 0 (legacy) or 2 (EIP-1559).
        coin_symbol (Optional[str]): the coin symbol.
        explorer (Optional[str]): the explorer URL.
        api (Optional[API]): an API instance.
        dex (Optional[DEX]): a DEX instance.

    """
    name: str
    rpc: str
    chain_id: Optional[int]
    tx_type: int
    coin_symbol: Optional[str]
    explorer: Optional[str]
    api: Optional[API]
    dex: Optional[DEX]

    def __init__(
            self, name: str, rpc: str, chain_id: Optional[int] = None, tx_type: int = 0,
            coin_symbol: Optional[str] = None, explorer: Optional[str] = None, api: Optional[API] = None,
            dex: Optional[DEX] = None
    ) -> None:
        """
        Initialize the class.

        Args:
            name (str): a network name.
            rpc (str): the RPC URL.
            chain_id (Optional[int]): the chain ID. (parsed automatically)
            tx_type (int): the main type of transactions in the network. Either 0 (legacy) or 2 (EIP-1559). (0)
            coin_symbol (Optional[str]): the coin symbol. (parsed from the network)
            explorer (Optional[str]): the explorer URL. (None)
            api (Optional[API]): an API instance. (None)
            dex (Optional[DEX]): a DEX instance. (None)

        """
        self.name = name.lower()
        self.rpc = rpc
        self.chain_id = chain_id
        self.tx_type = tx_type
        self.coin_symbol = coin_symbol
        self.explorer = explorer
        self.api = api
        self.dex = dex

        if not self.chain_id:
            try:
                self.chain_id = Web3(Web3.HTTPProvider(self.rpc)).eth.chain_id

            except:
                pass

        if not self.coin_symbol:
            try:
                response = requests.get('https://chainid.network/chains.json').json()
                network = next((network for network in response if network['chainId'] == self.chain_id), None)
                self.coin_symbol = network['nativeCurrency']['symbol']

            except:
                pass

        if self.coin_symbol:
            self.coin_symbol = self.coin_symbol.upper()

        self.set_api_functions()

    def set_api_functions(self) -> None:
        """
        Update API functions after API key change.
        """
        if self.api and self.api.key and self.api.url:
            self.api.functions = APIFunctions(self.api.key, self.api.url)

    def is_equal(self, network: Network) -> bool:
        """
        Compare chain IDs of two networks.

        Args:
            network (Network): the second network.

        Returns:
            bool: True if networks are equal.

        """
        return self.chain_id == network.chain_id


class Networks:
    """
    An instance with the most popular networks.
    """
    # Mainnets
    Ethereum = Network(
        name='ethereum',
        rpc='https://rpc.ankr.com/eth/',
        chain_id=1,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://etherscan.io/',
        api=API(key=config.ETHEREUM_API_KEY, url='https://api.etherscan.io/api', docs='https://docs.etherscan.io/'),
        dex=DEX(
            name='uniswap_v2', factory='0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
            router='0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'
        )
    )
    Arbitrum = Network(
        name='arbitrum',
        rpc='https://rpc.ankr.com/arbitrum/',
        chain_id=42161,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://arbiscan.io/',
        api=API(key=config.ARBITRUM_API_KEY, url='https://api.arbiscan.io/api', docs='https://docs.arbiscan.io/'),
        dex=DEX(
            name='uniswap_v3', factory='0x1F98431c8aD98523631AE4a59f267346ea31F984',
            router='0xE592427A0AEce92De3Edee1F18E0157C05861564'
        )
    )
    ArbitrumNova = Network(
        name='arbitrum_nova',
        rpc='https://nova.arbitrum.io/rpc/',
        chain_id=42170,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://nova.arbiscan.io/',
        api=API(
            key=config.ARBITRUM_API_KEY, url='https://api-nova.arbiscan.io/api', docs='https://nova.arbiscan.io/apis/'
        )
    )
    Optimism = Network(
        name='optimism',
        rpc='https://rpc.ankr.com/optimism/',
        chain_id=10,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://optimistic.etherscan.io/',
        api=API(
            key=config.OPTIMISM_API_KEY, url='https://api-optimistic.etherscan.io/api',
            docs='https://docs.optimism.etherscan.io/'
        ),
        dex=DEX(name='uniswap_v3', router='0xE592427A0AEce92De3Edee1F18E0157C05861564')
    )
    BSC = Network(
        name='bsc',
        rpc='https://rpc.ankr.com/bsc/',
        chain_id=56,
        tx_type=0,
        coin_symbol='BNB',
        explorer='https://bscscan.com/',
        api=API(key=config.BSC_API_KEY, url='https://api.bscscan.com/api', docs='https://docs.bscscan.com/'),
        dex=DEX(
            name='pancakeswap', factory='0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',
            router='0x10ED43C718714eb63d5aA57B78B54704E256024E'
        )
    )
    Polygon = Network(
        name='polygon',
        rpc='https://rpc.ankr.com/polygon/',
        chain_id=137,
        tx_type=2,
        coin_symbol='MATIC',
        explorer='https://polygonscan.com/',
        api=API(
            key=config.POLYGON_API_KEY, url='https://api.polygonscan.com/api', docs='https://docs.polygonscan.com/'
        ),
        dex=DEX(
            name='quickswap', factory='0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32',
            router='0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff'
        )
    )
    Avalanche = Network(
        name='avalanche',
        rpc='https://rpc.ankr.com/avalanche/',
        chain_id=43114,
        tx_type=2,
        coin_symbol='AVAX',
        explorer='https://snowtrace.io/',
        api=API(key=config.AVALANCHE_API_KEY, url='https://api.snowtrace.io/api', docs='https://docs.snowtrace.io/')
    )
    Moonbeam = Network(
        name='moonbeam',
        rpc='https://rpc.api.moonbeam.network/',
        chain_id=1284,
        tx_type=2,
        coin_symbol='GLMR',
        explorer='https://moonscan.io/',
        api=API(
            key=config.MOONBEAM_API_KEY, url='https://api-moonbeam.moonscan.io/api', docs='https://moonscan.io/apis/'
        )
    )
    Fantom = Network(
        name='fantom',
        rpc='https://rpc.ankr.com/fantom/',
        chain_id=250,
        tx_type=2,
        coin_symbol='FTM',
        explorer='https://ftmscan.com/',
        api=API(key=config.FANTOM_API_KEY, url='https://api.ftmscan.com/api', docs='https://docs.ftmscan.com/')
    )
    Celo = Network(
        name='celo',
        rpc='https://rpc.ankr.com/celo/',
        chain_id=42220,
        tx_type=0,
        coin_symbol='CELO',
        explorer='https://celoscan.io/',
        api=API(key=config.CELO_API_KEY, url='https://api.celoscan.io/api', docs='https://celoscan.io/apis/')
    )
    Gnosis = Network(
        name='gnosis',
        rpc='https://rpc.ankr.com/gnosis/',
        chain_id=100,
        tx_type=2,
        coin_symbol='xDAI',
        explorer='https://gnosisscan.io/',
        api=API(key=config.GNOSIS_API_KEY, url='https://api.gnosisscan.io/api', docs='https://docs.gnosisscan.io/')
    )
    HECO = Network(
        name='heco',
        rpc='https://http-mainnet.hecochain.com/',
        chain_id=128,
        tx_type=2,
        coin_symbol='HT',
        explorer='https://hecoinfo.com/',
        api=API(key=config.HECO_API_KEY, url='https://api.hecoinfo.com/api', docs='https://hecoinfo.com/apis')
    )

    # Testnets
    Goerli = Network(
        name='goerli',
        rpc='https://rpc.ankr.com/eth_goerli/',
        chain_id=5,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://goerli.etherscan.io/',
        api=API(
            key=config.GOERLI_API_KEY, url='https://api-goerli.etherscan.io/api',
            docs='https://docs.etherscan.io/v/goerli-etherscan/'
        )
    )

    Sepolia = Network(
        name='sepolia',
        rpc='https://rpc.ankr.com/eth_sepolia/',
        chain_id=11155111,
        tx_type=2,
        coin_symbol='ETH',
        explorer='https://sepolia.etherscan.io/',
        api=API(
            key=config.SEPOLIA_API_KEY, url='https://api-sepolia.etherscan.io/api',
            docs='https://docs.etherscan.io/v/sepolia-etherscan/'
        )
    )


class RawContract(AutoRepr):
    """
    An instance of a raw contract.

    Attributes:
        address (ChecksumAddress): a contract address.
        abi (List[Dict[str, Any]]): an ABI of the contract.

    """
    address: ChecksumAddress
    abi: List[Dict[str, Any]]

    def __init__(self, address: str, abi: Union[List[Dict[str, Any]], str]) -> None:
        """
        Initialize the class.

        Args:
            address (str): a contract address.
            abi (Union[List[Dict[str, Any]], str]): an ABI of the contract.

        """
        self.address = checksum(address)
        self.abi = json.loads(abi) if isinstance(abi, str) else abi


@dataclass
class CommonValues:
    """
    An instance with common values used in transactions.
    """
    Null: str = '0x0000000000000000000000000000000000000000000000000000000000000000'
    InfinityStr: str = '0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
    InfinityInt: int = int('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 16)


@dataclass
class DefaultABIs:
    """
    An instance with the default ABIs.
    """
    Token = [
        {
            'constant': True,
            'inputs': [],
            'name': 'name',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'symbol',
            'outputs': [{'name': '', 'type': 'string'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'totalSupply',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [],
            'name': 'decimals',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [{'name': 'who', 'type': 'address'}],
            'name': 'balanceOf',
            'outputs': [{'name': '', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': True,
            'inputs': [{'name': '_owner', 'type': 'address'}, {'name': '_spender', 'type': 'address'}],
            'name': 'allowance',
            'outputs': [{'name': 'remaining', 'type': 'uint256'}],
            'payable': False,
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'constant': False,
            'inputs': [{'name': '_spender', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}],
            'name': 'approve',
            'outputs': [],
            'payable': False,
            'stateMutability': 'nonpayable',
            'type': 'function'
        },
        {
            'constant': False,
            'inputs': [{'name': '_to', 'type': 'address'}, {'name': '_value', 'type': 'uint256'}],
            'name': 'transfer',
            'outputs': [], 'payable': False,
            'stateMutability': 'nonpayable',
            'type': 'function'
        }]
    NFT = [
        {
            'inputs': [],
            'name': 'name',
            'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'inputs': [],
            'name': 'symbol',
            'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'inputs': [],
            'name': 'totalSupply',
            'outputs': [{'internalType': 'uint256', 'name': '', 'type': 'uint256'}],
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}],
            'name': 'ownerOf',
            'outputs': [{'internalType': 'address', 'name': '', 'type': 'address'}],
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'inputs': [{'internalType': 'uint256', 'name': 'tokenId', 'type': 'uint256'}],
            'name': 'tokenURI',
            'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
            'stateMutability': 'view',
            'type': 'function'
        }]


@dataclass
class FunctionArgument:
    """
    An instance of a function argument.

    Attributes:
        name (str): an argument name.
        type (str): an argument type.

    """
    name: str
    type: str


@dataclass
class Function:
    """
    An instance of a function.

    Attributes:
        name (str): an argument name.
        inputs (List[FunctionArgument]): a list of input arguments.
        outputs (List[FunctionArgument]): a list of output arguments.

    """
    name: str
    inputs: List[FunctionArgument]
    outputs: List[FunctionArgument]


class ABI(AutoRepr):
    """
    An instance of an ABI.

    Attributes:
        abi (Union[List[Dict[str, Any]], str]): an ABI of a contract.
        functions (Optional[List[Function]]): a list of function instances.

    """
    abi: List[Dict[str, Any]]
    functions: Optional[List[Function]]

    def __init__(self, abi: Union[List[Dict[str, Any]], str]) -> None:
        """
        Initialize the class.

        Args:
            abi (Union[List[Dict[str, Any]], str]): an ABI of a contract.

        """
        self.abi = json.loads(abi) if isinstance(abi, str) else abi
        self.functions = None

        self.parse_functions(abi=self.abi)

    def parse_functions(self, abi: Union[List[Dict[str, Any]], str]) -> None:
        """
        Convert raw functions to instances.

        Args:
            abi (Union[List[Dict[str, Any]], str]): an ABI of a contract.

        """
        if not abi:
            return

        self.functions = []
        for function in abi:
            function_instance = Function(name=function.get('name'), inputs=[], outputs=[])
            inputs = function.get('inputs')
            if inputs:
                function_instance.inputs = [
                    FunctionArgument(name=input_.get('name'), type=input_.get('type')) for input_ in inputs
                ]

            outputs = function.get('outputs')
            if outputs:
                function_instance.outputs = [
                    FunctionArgument(name=output.get('name'), type=output.get('type')) for output in outputs
                ]

            self.functions.append(function_instance)


@dataclass
class NFTAttribute:
    """
    An instance of a NFT attribute.

    Attributes:
        name (str): an attribute name.
        value (Any): an attribute value.

    """
    name: str
    value: Any


class NFT(AutoRepr):
    """
    An instance of a NFT.

    Attributes:
        contract_address (ChecksumAddress): a contract address of a NFT collection.
        name (Optional[str]): the name of the NFT collection.
        symbol (Optional[str]): the symbol of the NFT collection.
        total_supply (Optional[int]): the total supply of the NFT collection.
        id (Optional[int]): an NFT ID.
        owner (Optional[str]): an owner of the NFT with specified ID.
        image_url (Optional[str]): an image URL of the NFT with specified ID.
        attributes (List[NFTAttribute]): a list of NFT attributes.

    """
    contract_address: ChecksumAddress
    name: Optional[str]
    symbol: Optional[str]
    total_supply: Optional[int]
    id: Optional[int]
    owner: Optional[str]
    image_url: Optional[str]
    attributes: List[NFTAttribute]

    def __init__(
            self, contract_address: str, name: Optional[str] = None, symbol: Optional[str] = None,
            total_supply: Optional[int] = None, id: Optional[int] = None, owner: Optional[str] = None,
            image_url: Optional[str] = None
    ) -> None:
        """
        Initialize the class.

        Args:
            contract_address (str): a contract address of a NFT collection.
            name (Optional[str]): the name of the NFT collection. (None)
            symbol (Optional[str]): the symbol of the NFT collection. (None)
            total_supply (Optional[int]): the total supply of the NFT collection. (None)
            id (Optional[int]): an NFT ID. (None)
            owner (Optional[str]): an owner of the NFT with specified ID. (None)
            image_url (Optional[str]): an image URL of the NFT with specified ID. (None)

        """
        self.contract_address = checksum(contract_address)
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.id = id
        self.owner = owner
        self.image_url = image_url
        self.attributes = []

    def parse_attributes(self, attributes: Optional[list]) -> None:
        """
        Convert raw attributes to instances.

        Args:
            attributes (Optional[list]): a list of attributes.

        """
        if not attributes:
            return

        self.attributes = []
        for attribute in attributes:
            name_key = list(attribute.keys())
            name_key.remove('value')
            name_key = name_key[0]
            attr_name = attribute[name_key]
            attr_value = attribute['value']
            self.attributes.append(NFTAttribute(name=attr_name, value=attr_value))


class HistoryTx:
    """
    An instance of a history transaction.
    """
    pass


class CoinTx(AutoRepr, HistoryTx):
    """
    An instance of a coin transaction.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize the class.

        Args:
            data (Dict[str, Any]): the dictionary with a coin transaction data.

        """
        self.hash: str = data.get('hash')
        self.from_: str = checksum(data.get('from'))
        self.to_: str = checksum(data.get('to'))
        self.contractAddress: str = checksum(data.get('contractAddress')) if data.get('contractAddress') else ''
        self.value: int = int(data.get('value'))
        self.methodId: str = data.get('methodId')
        self.functionName: str = data.get('functionName')
        self.isError: bool = bool(data.get('isError'))

        self.blockNumber: int = int(data.get('blockNumber'))
        self.timeStamp: int = int(data.get('timeStamp'))
        self.nonce: int = int(data.get('nonce'))
        self.blockHash: str = data.get('blockHash')
        self.transactionIndex: int = int(data.get('transactionIndex'))
        self.gas: int = int(data.get('gas'))
        self.gasUsed: int = int(data.get('gasUsed'))
        self.gasPrice: int = int(data.get('gasPrice'))
        self.txreceipt_status: int = int(data.get('txreceipt_status'))
        self.input: str = data.get('input')
        self.cumulativeGasUsed: int = int(data.get('cumulativeGasUsed'))
        self.confirmations: int = int(data.get('confirmations'))


class InternalTx(AutoRepr, HistoryTx):
    """
    An instance of an internal transaction.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize the class.

        Args:
            data (Dict[str, Any]): the dictionary with an internal transaction data.

        """
        self.hash: str = data.get('hash')
        self.from_: str = checksum(data.get('from'))
        self.to_: str = checksum(data.get('to'))
        self.contractAddress: str = checksum(data.get('contractAddress')) if data.get('contractAddress') else ''
        self.value: int = int(data.get('value'))
        self.isError: bool = bool(data.get('isError'))
        self.errCode: str = data.get('errCode')

        self.blockNumber: int = int(data.get('blockNumber'))
        self.timeStamp: int = int(data.get('timeStamp'))
        self.input: str = data.get('input')
        self.type: str = data.get('type')
        self.gas: int = int(data.get('gas'))
        self.gasUsed: int = int(data.get('gasUsed'))
        self.traceId: str = data.get('traceId')


class ERC20Tx(AutoRepr, HistoryTx):
    """
    An instance of a ERC20 transaction.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize the class.

        Args:
            data (Dict[str, Any]): the dictionary with a ERC20 transaction data.

        """
        self.hash: str = data.get('hash')
        self.from_: str = checksum(data.get('from'))
        self.to_: str = checksum(data.get('to'))
        self.contractAddress: str = checksum(data.get('contractAddress')) if data.get('contractAddress') else ''
        self.tokenName: str = data.get('tokenName')
        self.tokenSymbol: str = data.get('tokenSymbol')
        self.tokenDecimal: int = int(data.get('tokenDecimal'))
        self.value: int = int(data.get('value'))

        self.blockNumber: int = int(data.get('blockNumber'))
        self.timeStamp: int = int(data.get('timeStamp'))
        self.nonce: int = int(data.get('nonce'))
        self.blockHash: str = data.get('blockHash')
        self.transactionIndex: int = int(data.get('transactionIndex'))
        self.gas: int = int(data.get('gas'))
        self.gasPrice: int = int(data.get('gasPrice'))
        self.gasUsed: int = int(data.get('gasUsed'))
        self.cumulativeGasUsed: int = int(data.get('cumulativeGasUsed'))
        self.input: str = data.get('input')
        self.confirmations: int = int(data.get('confirmations'))


class ERC721Tx(AutoRepr, HistoryTx):
    """
    An instance of a ERC721 transaction.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize the class.

        Args:
            data (Dict[str, Any]): the dictionary with a ERC721 transaction data.

        """
        self.hash: str = data.get('hash')
        self.from_: str = checksum(data.get('from'))
        self.to_: str = checksum(data.get('to'))
        self.contractAddress: str = checksum(data.get('contractAddress')) if data.get('contractAddress') else ''
        self.tokenID: int = int(data.get('tokenID'))
        self.tokenName: str = data.get('tokenName')
        self.tokenSymbol: str = data.get('tokenSymbol')
        self.tokenDecimal: int = int(data.get('tokenDecimal'))

        self.blockNumber: int = int(data.get('blockNumber'))
        self.timeStamp: int = int(data.get('timeStamp'))
        self.nonce: int = int(data.get('nonce'))
        self.blockHash: str = data.get('blockHash')
        self.transactionIndex: int = int(data.get('transactionIndex'))
        self.gas: int = int(data.get('gas'))
        self.gasPrice: int = int(data.get('gasPrice'))
        self.gasUsed: int = int(data.get('gasUsed'))
        self.cumulativeGasUsed: int = int(data.get('cumulativeGasUsed'))
        self.input: str = data.get('input')
        self.confirmations: int = int(data.get('confirmations'))


class RawTxHistory(AutoRepr):
    """
    An instance of a raw transaction history.

    Attributes:
        address (ChecksumAddress): an address to which the history belongs.
        coin (List[Dict[str, Any]]): a list of transactions with coin.
        internal (List[Dict[str, Any]]): a list of internal transactions.
        erc20 (List[Dict[str, Any]]): a list of transactions with ERC20 tokens.
        erc721 (List[Dict[str, Any]]): a list of transactions with ERC721 tokens.

    """
    address: ChecksumAddress
    coin: List[Dict[str, Any]]
    internal: List[Dict[str, Any]]
    erc20: List[Dict[str, Any]]
    erc721: List[Dict[str, Any]]

    def __init__(
            self, address: str, coin_txs: List[Dict[str, Any]], internal_txs: List[Dict[str, Any]],
            erc20_txs: List[Dict[str, Any]], erc721_txs: List[Dict[str, Any]]
    ) -> None:
        """
        Initialize the class.

        Args:
            address (str): an address to which the history belongs.
            coin_txs (List[Dict[str, Any]]): a list of transactions with coin.
            internal_txs (List[Dict[str, Any]]): a list of internal transactions.
            erc20_txs (List[Dict[str, Any]]): a list of transactions with ERC20 tokens.
            erc721_txs (List[Dict[str, Any]]): a list of transactions with ERC721 tokens.

        """
        self.address = checksum(address)
        self.coin = coin_txs
        self.internal = internal_txs
        self.erc20 = erc20_txs
        self.erc721 = erc721_txs


@dataclass
class Txs:
    """
    An instance with transactions.

    Attributes:
        incoming (Dict[str, HistoryTx]): a dictionary with incoming transactions.
        outgoing (Dict[str, HistoryTx]): a dictionary with outgoing transactions.
        all (Dict[str, HistoryTx]): a dictionary with all transactions.

    """
    incoming: Dict[str, HistoryTx]
    outgoing: Dict[str, HistoryTx]
    all: Dict[str, HistoryTx]


class TxHistory(AutoRepr):
    """
    An instance of a transaction history.

    Attributes:
        address (str): an address to which the history belongs.
        coin (Optional[Txs]): a list of transactions with coin.
        internal (Optional[Txs]): a list of internal transactions.
        erc20 (Optional[Txs]): a list of transactions with ERC20 tokens.
        erc721 (Optional[Txs]): a list of transactions with ERC721 tokens.

    """
    address: ChecksumAddress
    coin: Optional[Txs]
    internal: Optional[Txs]
    erc20: Optional[Txs]
    erc721: Optional[Txs]

    def __init__(
            self, address: str, coin_txs: Optional[list] = None, internal_txs: Optional[list] = None,
            erc20_txs: Optional[list] = None, erc721_txs: Optional[list] = None
    ) -> None:
        """
        Initialize the class.

        Args:
            address (str): an address to which the history belongs.
            coin_txs (List[Dict[str, Any]]): a list of transactions with coin.
            internal_txs (List[Dict[str, Any]]): a list of internal transactions.
            erc20_txs (List[Dict[str, Any]]): a list of transactions with ERC20 tokens.
            erc721_txs (List[Dict[str, Any]]): a list of transactions with ERC721 tokens. (NFTs)

        """
        self.address = checksum(address)
        self.coin = None
        self.internal = None
        self.erc20 = None
        self.erc721 = None

        self.parse_coin_txs(txs=coin_txs)
        self.parse_internal_txs(txs=internal_txs)
        self.parse_erc20_txs(txs=erc20_txs)
        self.parse_erc721_txs(txs=erc721_txs)

    def parse_coin_txs(self, txs: Optional[list]) -> None:
        """
        Convert raw transactions with coin to instances.

        Args:
            txs (Optional[list]): a list of transactions with coin.

        """
        if not txs:
            return

        self.coin = Txs(incoming={}, outgoing={}, all={})
        for tx in txs:
            tx = CoinTx(data=tx)
            self.coin.all[tx.hash] = tx
            if tx.to_ == self.address:
                self.coin.incoming[tx.hash] = tx

            elif tx.from_ == self.address:
                self.coin.outgoing[tx.hash] = tx

    def parse_internal_txs(self, txs: Optional[list]) -> None:
        """
        Convert raw internal transactions to instances.

        Args:
            txs (Optional[list]): a list of internal transactions.

        """
        if not txs:
            return

        self.internal = Txs(incoming={}, outgoing={}, all={})
        for tx in txs:
            tx = InternalTx(data=tx)
            self.internal.all[tx.hash] = tx
            if tx.to_ == self.address:
                self.internal.incoming[tx.hash] = tx

            elif tx.from_ == self.address:
                self.internal.outgoing[tx.hash] = tx

    def parse_erc20_txs(self, txs: Optional[list]) -> None:
        """
        Convert raw transactions with ERC20 tokens to instances.

        Args:
            txs (Optional[list]): a list of transactions with ERC20 tokens.

        """
        if not txs:
            return

        self.erc20 = Txs(incoming={}, outgoing={}, all={})
        for tx in txs:
            tx = ERC20Tx(data=tx)
            self.erc20.all[tx.hash] = tx
            if tx.to_ == self.address:
                self.erc20.incoming[tx.hash] = tx

            elif tx.from_ == self.address:
                self.erc20.outgoing[tx.hash] = tx

    def parse_erc721_txs(self, txs: Optional[list]) -> None:
        """
        Convert raw transactions with ERC721 tokens (NFTs) to instances.

        Args:
            txs (Optional[list]): a list of transactions with ERC721 tokens (NFTs).

        """
        if not txs:
            return

        self.erc721 = Txs(incoming={}, outgoing={}, all={})
        for tx in txs:
            tx = ERC721Tx(data=tx)
            self.erc721.all[tx.hash] = tx
            if tx.to_ == self.address:
                self.erc721.incoming[tx.hash] = tx

            elif tx.from_ == self.address:
                self.erc721.outgoing[tx.hash] = tx


class TxArgs(AutoRepr):
    """
    An instance for named transaction arguments.
    """

    def __init__(self, **kwargs) -> None:
        """
        Initialize the class.

        Args:
            **kwargs: named arguments of a contract transaction.

        """
        self.__dict__.update(kwargs)

    def list(self) -> List[Any]:
        """
        Get list of transaction arguments.

        Returns:
            List[Any]: list of transaction arguments.

        """
        return list(self.__dict__.values())

    def tuple(self) -> Tuple[Any]:
        """
        Get tuple of transaction arguments.

        Returns:
            Tuple[Any]: tuple of transaction arguments.

        """
        return tuple(self.__dict__.values())


class Unit(AutoRepr):
    """
    An instance of an Ethereum unit.

    Attributes:
        unit (str): a unit name.
        decimals (int): a number of decimals.
        Wei (int): the amount in Wei.
        KWei (Decimal): the amount in KWei.
        MWei (Decimal): the amount in MWei.
        GWei (Decimal): the amount in GWei.
        Szabo (Decimal): the amount in Szabo.
        Finney (Decimal): the amount in Finney.
        Ether (Decimal): the amount in Ether.
        KEther (Decimal): the amount in KEther.
        MEther (Decimal): the amount in MEther.
        GEther (Decimal): the amount in GEther.
        TEther (Decimal): the amount in TEther.

    """
    unit: str
    decimals: int
    Wei: int
    KWei: Decimal
    MWei: Decimal
    GWei: Decimal
    Szabo: Decimal
    Finney: Decimal
    Ether: Decimal
    KEther: Decimal
    MEther: Decimal
    GEther: Decimal
    TEther: Decimal

    def __init__(self, amount: Union[int, float, str, Decimal], unit: str) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.
            unit (str): a unit name.

        """
        self.unit = unit
        self.decimals = 18
        self.Wei = to_wei(amount, self.unit)
        self.KWei = from_wei(self.Wei, 'kwei')
        self.MWei = from_wei(self.Wei, 'mwei')
        self.GWei = from_wei(self.Wei, 'gwei')
        self.Szabo = from_wei(self.Wei, 'szabo')
        self.Finney = from_wei(self.Wei, 'finney')
        self.Ether = from_wei(self.Wei, 'ether')
        self.KEther = from_wei(self.Wei, 'kether')
        self.MEther = from_wei(self.Wei, 'mether')
        self.GEther = from_wei(self.Wei, 'gether')
        self.TEther = from_wei(self.Wei, 'tether')

    def __add__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return Wei(self.Wei + other.Wei)

        elif isinstance(other, int):
            return Wei(self.Wei + other)

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return GWei(self.GWei + GWei(other).GWei)

            else:
                return Ether(self.Ether + Ether(other).Ether)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __radd__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return Wei(other.Wei + self.Wei)

        elif isinstance(other, int):
            return Wei(other + self.Wei)

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return GWei(GWei(other).GWei + self.GWei)

            else:
                return Ether(Ether(other).Ether + self.Ether)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __sub__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return Wei(self.Wei - other.Wei)

        elif isinstance(other, int):
            return Wei(self.Wei - other)

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return GWei(self.GWei - GWei(other).GWei)

            else:
                return Ether(self.Ether - Ether(other).Ether)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __rsub__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return Wei(other.Wei - self.Wei)

        elif isinstance(other, int):
            return Wei(other - self.Wei)

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return GWei(GWei(other).GWei - self.GWei)

            else:
                return Ether(Ether(other).Ether - self.Ether)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __mul__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return Wei(self.Wei * other.Wei)

        elif isinstance(other, int):
            return Wei(self.Wei * other)

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return GWei(self.GWei * GWei(other).GWei)

            else:
                return Ether(self.Ether * Ether(other).Ether)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __rmul__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return Wei(other.Wei * self.Wei)

        elif isinstance(other, int):
            return Wei(other * self.Wei)

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return GWei(GWei(other).GWei * self.GWei)

            else:
                return Ether(Ether(other).Ether * self.Ether)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __truediv__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return Wei(self.Wei / other.Wei)

        elif isinstance(other, int):
            return Wei(self.Wei / Decimal(str(other)))

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return GWei(self.GWei / GWei(other).GWei)

            else:
                return Ether(self.Ether / Ether(other).Ether)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __rtruediv__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return Wei(other.Wei / self.Wei)

        elif isinstance(other, int):
            return Wei(Decimal(str(other)) / self.Wei)

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return GWei(GWei(other).GWei / self.GWei)

            else:
                return Ether(Ether(other).Ether / self.Ether)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __iadd__(self, other):
        return self.__add__(other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __itruediv__(self, other):
        return self.__truediv__(other)

    def __lt__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei < other.Wei

        elif isinstance(other, int):
            return self.Wei < other

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return self.GWei < GWei(other).GWei

            else:
                return self.Ether < Ether(other).Ether

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __le__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei <= other.Wei

        elif isinstance(other, int):
            return self.Wei <= other

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return self.GWei <= GWei(other).GWei

            else:
                return self.Ether <= Ether(other).Ether

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __eq__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei == other.Wei

        elif isinstance(other, int):
            return self.Wei == other

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return self.GWei == GWei(other).GWei

            else:
                return self.Ether == Ether(other).Ether

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __ne__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei != other.Wei

        elif isinstance(other, int):
            return self.Wei != other

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return self.GWei != GWei(other).GWei

            else:
                return self.Ether != Ether(other).Ether

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __gt__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei > other.Wei

        elif isinstance(other, int):
            return self.Wei > other

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return self.GWei > GWei(other).GWei

            else:
                return self.Ether > Ether(other).Ether

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __ge__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei >= other.Wei

        elif isinstance(other, int):
            return self.Wei >= other

        elif isinstance(other, float):
            if self.unit == 'gwei':
                return self.GWei >= GWei(other).GWei

            else:
                return self.Ether >= Ether(other).Ether

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")


class Wei(Unit):
    """
    An instance of a Wei unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'wei')


class KWei(Unit):
    """
    An instance of a KWei unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'kwei')


class MWei(Unit):
    """
    An instance of a MWei unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'mwei')


class GWei(Unit):
    """
    An instance of a GWei unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'gwei')


class Szabo(Unit):
    """
    An instance of a Szabo unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'szabo')


class Finney(Unit):
    """
    An instance of a Finney unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'finney')


class Ether(Unit):
    """
    An instance of an Ether unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'ether')


class KEther(Unit):
    """
    An instance of a KEther unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'kether')


class MEther(Unit):
    """
    An instance of a MEther unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'mether')


class GEther(Unit):
    """
    An instance of a GEther unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'gether')


class TEther(Unit):
    """
    An instance of a TEther unit.
    """

    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.

        """
        super().__init__(amount, 'tether')


class TokenAmount(AutoRepr):
    """
    An instance of a token amount.

    Attributes:
        decimals (int): a number of decimals of the token.
        Wei (int): the amount in Wei.
        Ether (Decimal): the amount in Ether.

    """
    decimals: int
    Wei: int
    Ether: Decimal

    def __init__(self, amount: Union[int, float, str, Decimal], decimals: int = 18, wei: bool = False) -> None:
        """
        Initialize the class.

        Args:
            amount (Union[int, float, str, Decimal]): an amount.
            decimals (int): the number of decimals of the token. (18)
            wei (bool): the 'amount' is specified in Wei. (False)

        """
        if wei:
            self.Wei = amount
            self.Ether = Decimal(str(amount)) / 10 ** decimals

        else:
            self.Wei = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether = Decimal(str(amount))

        self.decimals = decimals

    def change_decimals(self, new_decimals: int) -> int:
        """
        Leave the Ether amount and change the Wei based on the new decimals.

        Args:
            new_decimals (int): the new number of decimals.

        Returns:
            int: the amount in Wei.

        """
        self.Wei: int = int(self.Ether * 10 ** new_decimals)
        self.decimals = new_decimals
        return self.Wei

    def __add__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return TokenAmount(self.Ether + other.Ether, decimals=self.decimals)

        elif isinstance(other, int):
            return TokenAmount(self.Wei + other, decimals=self.decimals, wei=True)

        elif isinstance(other, float):
            return TokenAmount(self.Ether + TokenAmount(other, decimals=self.decimals).Ether, decimals=self.decimals)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __radd__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return TokenAmount(other.Ether + self.Ether, decimals=self.decimals)

        elif isinstance(other, int):
            return TokenAmount(other + self.Wei, decimals=self.decimals, wei=True)

        elif isinstance(other, float):
            return TokenAmount(TokenAmount(other, decimals=self.decimals).Ether + self.Ether, decimals=self.decimals)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __sub__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return TokenAmount(self.Ether - other.Ether, decimals=self.decimals)

        elif isinstance(other, int):
            return TokenAmount(self.Wei - other, decimals=self.decimals, wei=True)

        elif isinstance(other, float):
            return TokenAmount(self.Ether - TokenAmount(other, decimals=self.decimals).Ether, decimals=self.decimals)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __rsub__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return TokenAmount(other.Ether - self.Ether, decimals=self.decimals)

        elif isinstance(other, int):
            return TokenAmount(other - self.Wei, decimals=self.decimals, wei=True)

        elif isinstance(other, float):
            return TokenAmount(TokenAmount(other, decimals=self.decimals).Ether - self.Ether, decimals=self.decimals)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __mul__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return TokenAmount(self.Ether * other.Ether, decimals=self.decimals)

        elif isinstance(other, int):
            return TokenAmount(self.Wei * other, decimals=self.decimals, wei=True)

        elif isinstance(other, float):
            return TokenAmount(self.Ether * TokenAmount(other, decimals=self.decimals).Ether, decimals=self.decimals)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __rmul__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return TokenAmount(other.Ether * self.Ether, decimals=self.decimals)

        elif isinstance(other, int):
            return TokenAmount(other * self.Wei, decimals=self.decimals, wei=True)

        elif isinstance(other, float):
            return TokenAmount(TokenAmount(other, decimals=self.decimals).Ether * self.Ether, decimals=self.decimals)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __truediv__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return TokenAmount(self.Ether / other.Ether, decimals=self.decimals)

        elif isinstance(other, int):
            return TokenAmount(self.Wei / other, decimals=self.decimals, wei=True)

        elif isinstance(other, float):
            return TokenAmount(self.Ether / TokenAmount(other, decimals=self.decimals).Ether, decimals=self.decimals)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __rtruediv__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return TokenAmount(other.Ether / self.Ether, decimals=self.decimals)

        elif isinstance(other, int):
            return TokenAmount(other / self.Wei, decimals=self.decimals, wei=True)

        elif isinstance(other, float):
            return TokenAmount(TokenAmount(other, decimals=self.decimals).Ether / self.Ether, decimals=self.decimals)

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __iadd__(self, other):
        return self.__add__(other)

    def __isub__(self, other):
        return self.__sub__(other)

    def __imul__(self, other):
        return self.__mul__(other)

    def __itruediv__(self, other):
        return self.__truediv__(other)

    def __lt__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei < other.Wei

        elif isinstance(other, int):
            return self.Wei < other

        elif isinstance(other, float):
            return self.Wei < TokenAmount(other, decimals=self.decimals).Wei

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __le__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei <= other.Wei

        elif isinstance(other, int):
            return self.Wei <= other

        elif isinstance(other, float):
            return self.Wei <= TokenAmount(other, decimals=self.decimals).Wei

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __eq__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei == other.Wei

        elif isinstance(other, int):
            return self.Wei == other

        elif isinstance(other, float):
            return self.Wei == TokenAmount(other, decimals=self.decimals).Wei

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __ne__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei != other.Wei

        elif isinstance(other, int):
            return self.Wei != other

        elif isinstance(other, float):
            return self.Wei != TokenAmount(other, decimals=self.decimals).Wei

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __gt__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei > other.Wei

        elif isinstance(other, int):
            return self.Wei > other

        elif isinstance(other, float):
            return self.Wei > TokenAmount(other, decimals=self.decimals).Wei

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")

    def __ge__(self, other):
        if isinstance(other, (Unit, TokenAmount)):
            if self.decimals != other.decimals:
                raise ArithmeticError('The values have different decimals!')

            return self.Wei >= other.Wei

        elif isinstance(other, int):
            return self.Wei >= other

        elif isinstance(other, float):
            return self.Wei >= TokenAmount(other, decimals=self.decimals).Wei

        else:
            raise ArithmeticError(f"{type(other)} type isn't supported!")
