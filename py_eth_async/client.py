import random
from typing import Optional

from eth_account.signers.local import LocalAccount
from web3 import Web3

from py_eth_async.contracts import Contracts
from py_eth_async.data.models import Network, Networks
from py_eth_async.nfts import NFTs
from py_eth_async.transactions import Transactions
from py_eth_async.wallet import Wallet


class Client:
    network: Network
    account: Optional[LocalAccount]
    w3: Web3

    def __init__(self, private_key: Optional[str] = None, network: Network = Networks.Goerli) -> None:
        """
        Initialize the client that is used to interact with all functions.

        :param str private_key: a private key of a wallet, specify '' in order not to import the wallet (generate a new one)
        :param Network network: a network instance (Goerli)
        """
        self.network = network
        self.w3 = Web3(Web3.AsyncHTTPProvider(self.network.rpc))
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key=private_key)

        elif private_key is None:
            self.account = self.w3.eth.account.create(extra_entropy=str(random.randint(1, 999_999_999)))

        else:
            self.account = None

        self.contracts = Contracts(self)
        self.nfts = NFTs(self)
        self.transactions = Transactions(self)
        self.wallet = Wallet(self)
