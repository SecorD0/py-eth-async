import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Union, Dict, List, Any

import requests
from eth_utils import to_wei, from_wei
from pretty_utils.type_functions.classes import AutoRepr
from web3 import Web3

from py_eth_async import config
from py_eth_async.explorer_api import APIFunctions
from py_eth_async.utils import checksum


@dataclass
class API:
    """
    An API related information.

    :param str key: an API-key
    :param str url: an API entrypoint URL
    :param str docs: a docs URL
    :param Optional[APIFunctions] functions: the functions instance (None)
    """
    key: str
    url: str
    docs: str
    functions: Optional[APIFunctions] = None


@dataclass
class DEX:
    """
    A DEX related information.

    :param str name: a DEX name
    :param Optional[str] factory: a factory contract address
    :param Optional[str] router: a router contract address
    """
    name: str
    factory: Optional[str] = None
    router: Optional[str] = None


class Network(AutoRepr):
    def __init__(self, name: str, rpc: str, coin_symbol: Optional[str] = None, explorer: Optional[str] = None,
                 api: Optional[API] = None, dex: Optional[DEX] = None) -> None:
        """
        A Network instance to use it in the Client.

        :param str name: a network name
        :param str rpc: the RPC URL
        :param str coin_symbol: the coin symbol (parsed from the network)
        :param Optional[str] explorer: the explorer URL (None)
        :param Optional[API] api: an API instance (None)
        :param Optional[DEX] dex: a DEX instance (None)
        """
        self.name: str = name.lower()
        self.rpc: str = rpc
        self.coin_symbol: str = coin_symbol
        self.explorer: Optional[str] = explorer
        self.api: Optional[API] = api
        self.dex: Optional[DEX] = dex

        if not self.coin_symbol:
            try:
                chain_id = Web3(Web3.HTTPProvider(self.rpc)).eth.chain_id
                response = requests.get('https://chainid.network/chains.json').json()
                network = next((network for network in response if network['chainId'] == chain_id), None)
                self.coin_symbol = network['nativeCurrency']['symbol']

            except:
                pass

        if self.coin_symbol:
            self.coin_symbol = self.coin_symbol.upper()

        if api:
            self.api.functions = APIFunctions(api.key, api.url)


class Networks:
    """
    The most popular networks.
    """
    # Mainnets
    Ethereum = Network(name='ethereum',
                       rpc='https://rpc.ankr.com/eth/',
                       coin_symbol='ETH',
                       explorer='https://etherscan.io/',
                       api=API(key=config.ETHEREUM_APIKEY,
                               url='https://api.etherscan.io/api',
                               docs='https://docs.etherscan.io/'),
                       dex=DEX(name='uniswap_v2',
                               factory='0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
                               router='0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'))
    Arbitrum = Network(name='arbitrum',
                       rpc='https://arb1.arbitrum.io/rpc/',
                       coin_symbol='ETH',
                       explorer='https://arbiscan.io/',
                       api=API(key=config.ARBITRUM_APIKEY,
                               url='https://api.arbiscan.io/api',
                               docs='https://docs.arbiscan.io/'),
                       dex=DEX(name='uniswap_v3',
                               factory='0x1F98431c8aD98523631AE4a59f267346ea31F984',
                               router='0xE592427A0AEce92De3Edee1F18E0157C05861564'))
    ArbitrumNova = Network(name='arbitrum_nova',
                           rpc='https://nova.arbitrum.io/rpc/',
                           coin_symbol='ETH',
                           explorer='https://nova.arbiscan.io/',
                           api=API(key=config.ARBITRUM_APIKEY,
                                   url='https://api-nova.arbiscan.io/api',
                                   docs='https://nova.arbiscan.io/apis/'))
    Optimism = Network(name='optimism',
                       rpc='https://rpc.ankr.com/optimism/',
                       coin_symbol='ETH',
                       explorer='https://optimistic.etherscan.io/',
                       api=API(key=config.OPTIMISM_APIKEY,
                               url='https://api-optimistic.etherscan.io/api',
                               docs='https://docs.optimism.etherscan.io/'),
                       dex=DEX(name='uniswap_v3',
                               router='0xE592427A0AEce92De3Edee1F18E0157C05861564'))
    BSC = Network(name='bsc',
                  rpc='https://bsc-dataseed.binance.org/',
                  coin_symbol='BNB',
                  explorer='https://bscscan.com/',
                  api=API(key=config.BSC_APIKEY,
                          url='https://api.bscscan.com/api',
                          docs='https://docs.bscscan.com/'),
                  dex=DEX(name='pancakeswap',
                          factory='0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',
                          router='0x10ED43C718714eb63d5aA57B78B54704E256024E'))
    Matic = Network(name='matic',
                    rpc='https://polygon-rpc.com/',
                    coin_symbol='MATIC',
                    explorer='https://polygonscan.com/',
                    api=API(key=config.MATIC_APIKEY,
                            url='https://api.polygonscan.com/api',
                            docs='https://docs.polygonscan.com/'),
                    dex=DEX(name='quickswap',
                            factory='0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32',
                            router='0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff'))
    Avalanche = Network(name='avalanche',
                        rpc='https://api.avax.network/ext/bc/C/rpc/',
                        coin_symbol='AVAX',
                        explorer='https://snowtrace.io/',
                        api=API(key=config.AVALANCHE_APIKEY,
                                url='https://api.snowtrace.io/api',
                                docs='https://docs.snowtrace.io/'))
    Moonbeam = Network(name='moonbeam',
                       rpc='https://rpc.api.moonbeam.network/',
                       coin_symbol='GLMR',
                       explorer='https://moonscan.io/',
                       api=API(key=config.MOONBEAM_APIKEY,
                               url='https://api-moonbeam.moonscan.io/api',
                               docs='https://moonscan.io/apis/'))
    Fantom = Network(name='fantom',
                     rpc='https://rpc.ankr.com/fantom/',
                     coin_symbol='FTM',
                     explorer='https://ftmscan.com/',
                     api=API(key=config.FANTOM_APIKEY,
                             url='https://api.ftmscan.com/api',
                             docs='https://docs.ftmscan.com/'))
    Gnosis = Network(name='gnosis',
                     rpc='https://rpc.ankr.com/gnosis/',
                     coin_symbol='xDAI',
                     explorer='https://gnosisscan.io/',
                     api=API(key=config.GNOSIS_APIKEY,
                             url='https://api.gnosisscan.io/api',
                             docs='https://docs.gnosisscan.io/'))
    HECO = Network(name='heco',
                   rpc='https://http-mainnet.hecochain.com/',
                   coin_symbol='HT',
                   explorer='https://hecoinfo.com/',
                   api=API(key=config.HECO_APIKEY,
                           url='https://api.hecoinfo.com/api',
                           docs='https://hecoinfo.com/apis'))

    # Testnets
    Goerli = Network(name='goerli',
                     rpc='https://rpc.ankr.com/eth_goerli/',
                     coin_symbol='ETH',
                     explorer='https://goerli.etherscan.io/',
                     api=API(key=config.GOERLI_APIKEY,
                             url='https://api-goerli.etherscan.io/api',
                             docs='https://docs.etherscan.io/v/goerli-etherscan/'))

    Sepolia = Network(name='sepolia',
                      rpc='https://rpc.ankr.com/eth_sepolia/',
                      coin_symbol='ETH',
                      explorer='https://sepolia.etherscan.io/',
                      api=API(key=config.SEPOLIA_APIKEY,
                              url='https://api-sepolia.etherscan.io/api',
                              docs='https://docs.etherscan.io/v/sepolia-etherscan/'))


@dataclass
class CommonValues:
    """
    Common values used in transactions.
    """
    Null: str = '0x0000000000000000000000000000000000000000000000000000000000000000'
    InfinityStr: str = '0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
    InfinityInt: int = int('0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 16)


@dataclass
class DefaultABIs:
    """
    The default ABIs.
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
    A function argument.

    :param str name: an argument name
    :param str type: an argument type
    """
    name: str
    type: str


@dataclass
class Function:
    """
    A function instance.

    :param str name: an argument name
    :param List[FunctionArgument] inputs: a list of input arguments
    :param List[FunctionArgument] outputs: a list of output arguments
    """
    name: str
    inputs: List[FunctionArgument]
    outputs: List[FunctionArgument]


class ABI(AutoRepr):
    def __init__(self, abi: Union[str, list]) -> None:
        """
        An ABI instance.

        :param Union[str, list] abi: an ABI of a contract
        """
        if isinstance(abi, str):
            abi = json.loads(abi)

        self.abi: list = abi
        self.functions: Optional[List[Function]] = None

        self.parse_functions(abi=self.abi)

    def parse_functions(self, abi: list) -> None:
        """
        Convert raw functions to instances.

        :param list abi: an ABI of a contract
        """
        if not abi:
            return

        self.functions = []
        for function in abi:
            function_instance = Function(name=function.get('name'), inputs=[], outputs=[])
            inputs = function.get('inputs')
            if inputs:
                function_instance.inputs = [FunctionArgument(name=input_.get('name'), type=input_.get('type')) for
                                            input_ in inputs]

            outputs = function.get('outputs')
            if outputs:
                function_instance.outputs = [FunctionArgument(name=output.get('name'), type=output.get('type')) for
                                             output in outputs]

            self.functions.append(function_instance)


@dataclass
class NFTAttribute:
    """
    A NFT attribute.

    :param str name: an attribute name
    :param Any value: an attribute value
    """
    name: str
    value: Any


class NFT(AutoRepr):
    def __init__(self, contract_address: str, name: Optional[str] = None, symbol: Optional[str] = None,
                 total_supply: Optional[int] = None, id: Optional[int] = None, owner: Optional[str] = None,
                 image_url: Optional[str] = None) -> None:
        """
        A NFT instance.

        :param str contract_address: a contract address of a NFT collection
        :param Optional[str] name: the name of the NFT collection (None)
        :param Optional[str] symbol: the symbol of the NFT collection (None)
        :param Optional[int] total_supply: the total supply of the NFT collection (None)
        :param Optional[int] id: an NFT ID (None)
        :param Optional[str] owner: an owner of the NFT with specified ID (None)
        :param Optional[str] image_url: an image URL of the NFT with specified ID (None)
        """
        self.contract_address: str = contract_address
        self.name: Optional[str] = name
        self.symbol: Optional[str] = symbol
        self.total_supply: Optional[int] = total_supply
        self.id: Optional[int] = id
        self.owner: Optional[str] = owner
        self.image_url: Optional[str] = image_url
        self.attributes: List[NFTAttribute] = []

    def parse_attributes(self, attributes: Optional[list]) -> None:
        """
        Convert raw attributes to instances.

        :param Optional[list] attributes: a list of attributes
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
    pass


class CoinTx(AutoRepr, HistoryTx):
    def __init__(self, data: dict) -> None:
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
    def __init__(self, data: dict) -> None:
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
    def __init__(self, data: dict) -> None:
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
    def __init__(self, data: dict) -> None:
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
    def __init__(self, address: str, coin_txs: List[Dict[str, Any]], internal_txs: List[Dict[str, Any]],
                 erc20_txs: List[Dict[str, Any]], erc721_txs: List[Dict[str, Any]]) -> None:
        """
        A raw transaction history instance.

        :param str address: an address to which the history belongs
        :param List[Dict[str, Any]] coin_txs: a list of transactions with coin
        :param List[Dict[str, Any]] internal_txs: a list of internal transactions
        :param List[Dict[str, Any]] erc20_txs: a list of transactions ERC20 tokens
        :param List[Dict[str, Any]] erc721_txs: a list of transactions ERC721 tokens (NFTs)
        """
        self.address: str = checksum(address)
        self.coin: List[Dict[str, Any]] = coin_txs
        self.internal: List[Dict[str, Any]] = internal_txs
        self.erc20: List[Dict[str, Any]] = erc20_txs
        self.erc721: List[Dict[str, Any]] = erc721_txs


@dataclass
class Txs:
    """
    An instance with transactions.

    :param Dict[str, HistoryTx] incoming: a dictionary with incoming transactions
    :param Dict[str, HistoryTx] outgoing: a dictionary with outgoing transactions
    :param Dict[str, HistoryTx] all: a dictionary with all transactions
    """
    incoming: Dict[str, HistoryTx]
    outgoing: Dict[str, HistoryTx]
    all: Dict[str, HistoryTx]


class TxHistory(AutoRepr):
    def __init__(self, address: str, coin_txs: Optional[list] = None, internal_txs: Optional[list] = None,
                 erc20_txs: Optional[list] = None, erc721_txs: Optional[list] = None) -> None:
        """
        A transaction history instance.

        :param str address: an address to which the history belongs
        :param List[Dict[str, Any]] coin_txs: a list of transactions with coin
        :param List[Dict[str, Any]] internal_txs: a list of internal transactions
        :param List[Dict[str, Any]] erc20_txs: a list of transactions with ERC20 tokens
        :param List[Dict[str, Any]] erc721_txs: a list of transactions with ERC721 tokens (NFTs)
        """
        self.address: str = checksum(address)
        self.coin: Optional[Txs] = None
        self.internal: Optional[Txs] = None
        self.erc20: Optional[Txs] = None
        self.erc721: Optional[Txs] = None

        self.parse_coin_txs(txs=coin_txs)
        self.parse_internal_txs(txs=internal_txs)
        self.parse_erc20_txs(txs=erc20_txs)
        self.parse_erc721_txs(txs=erc721_txs)

    def parse_coin_txs(self, txs: Optional[list]) -> None:
        """
        Convert raw transactions with coin to instances.

        :param Optional[list] txs: a list of transactions with coin
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

        :param Optional[list] txs: a list of internal transactions
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

        :param Optional[list] txs: a list of transactions with ERC20 tokens
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

        :param Optional[list] txs: a list of transactions with ERC721 tokens (NFTs)
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


class Unit(AutoRepr):
    def __init__(self, amount: Union[int, float, str, Decimal], unit: str) -> None:
        """
        An Ethereum unit.

        :param Union[int, float, str, Decimal] amount: an amount
        :param str unit: a unit name
        """
        self.Wei: int = to_wei(amount, unit)
        self.KWei: Decimal = from_wei(self.Wei, 'kwei')
        self.MWei: Decimal = from_wei(self.Wei, 'mwei')
        self.GWei: Decimal = from_wei(self.Wei, 'gwei')
        self.Szabo: Decimal = from_wei(self.Wei, 'szabo')
        self.Finney: Decimal = from_wei(self.Wei, 'finney')
        self.Ether: Decimal = from_wei(self.Wei, 'ether')
        self.KEther: Decimal = from_wei(self.Wei, 'kether')
        self.MEther: Decimal = from_wei(self.Wei, 'mether')
        self.GEther: Decimal = from_wei(self.Wei, 'gether')
        self.TEther: Decimal = from_wei(self.Wei, 'tether')


class Wei(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The Wei unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'wei')


class KWei(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The KWei unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'kwei')


class MWei(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The MWei unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'mwei')


class GWei(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The GWei unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'gwei')


class Szabo(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The Szabo unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'szabo')


class Finney(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The Finney unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'finney')


class Ether(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The Ether unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'ether')


class KEther(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The KEther unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'kether')


class MEther(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The MEther unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'mether')


class GEther(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The GEther unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'gether')


class TEther(Unit):
    def __init__(self, amount: Union[int, float, str, Decimal]) -> None:
        """
        The TEther unit.

        :param Union[int, float, str, Decimal] amount: an amount
        """
        super().__init__(amount, 'tether')


class TokenAmount(AutoRepr):
    Wei: int
    Ether: Decimal
    decimals: int

    def __init__(self, amount: Union[int, float, str, Decimal], decimals: int = 18, wei: bool = False) -> None:
        """
        A token amount instance.

        :param Union[int, float, str, Decimal] amount: an amount
        :param int decimals: the decimals of the token (18)
        :param bool wei: the 'amount' is specified in Wei (False)
        """
        if wei:
            self.Wei: int = amount
            self.Ether: Decimal = Decimal(str(amount)) / 10 ** decimals

        else:
            self.Wei: int = int(Decimal(str(amount)) * 10 ** decimals)
            self.Ether: Decimal = Decimal(str(amount))

        self.decimals = decimals

    def change_decimals(self, new_decimals: int) -> int:
        """
        Leave the Ether amount and change the Wei based on the new decimals.

        :param int new_decimals: the new decimals
        :return int: the amount in Wei
        """
        self.Wei: int = int(self.Ether * 10 ** new_decimals)
        self.decimals = new_decimals
        return self.Wei
