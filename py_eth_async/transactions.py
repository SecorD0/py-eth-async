from typing import Union, Optional, Dict, Any, Tuple

from eth_account.datastructures import SignedTransaction, SignedMessage
from eth_account.messages import encode_defunct
from hexbytes import HexBytes
from pretty_utils.type_functions.classes import AutoRepr
from web3.contract import AsyncContract
from web3.types import TxReceipt, _Hash32, TxParams, Address

from py_eth_async import exceptions
from py_eth_async.data import types
from py_eth_async.data.models import (
    TxHistory, RawTxHistory, GWei, Wei, Ether, TokenAmount, CommonValues, CoinTx, TxArgs
)
from py_eth_async.data.types import Web3Async
from py_eth_async.utils import api_key_required, checksum


class Tx(AutoRepr):
    """
    An instance of transaction for easy execution of actions on it.

    Attributes:
        hash (Optional[_Hash32]): a transaction hash.
        params (Optional[dict]): the transaction parameters.
        receipt (Optional[TxReceipt]): a transaction receipt.
        function_identifier (Optional[str]): a function identifier.
        input_data (Optional[Dict[str, Any]]): an input data.

    """
    hash: Optional[_Hash32]
    params: Optional[dict]
    receipt: Optional[TxReceipt]
    function_identifier: Optional[str]
    input_data: Optional[Dict[str, Any]]

    def __init__(self, tx_hash: Optional[Union[str, _Hash32]] = None, params: Optional[dict] = None) -> None:
        """
        Initialize the class.

        Args:
            tx_hash (Optional[Union[str, _Hash32]]): the transaction hash. (None)
            params (Optional[dict]): a dictionary with transaction parameters. (None)

        """
        if not tx_hash and not params:
            raise exceptions.TransactionException("Specify 'tx_hash' or 'params' argument values!")

        if isinstance(tx_hash, str):
            tx_hash = HexBytes(tx_hash)

        self.hash = tx_hash
        self.params = params
        self.receipt = None
        self.function_identifier = None
        self.input_data = None

    async def parse_params(self, client) -> Dict[str, Any]:
        """
        Parse the parameters of a sent transaction.

        Args:
            client (Client): the Client instance.

        Returns:
            Dict[str, Any]: the parameters of a sent transaction.

        """
        tx_data = await client.w3.eth.get_transaction(transaction_hash=self.hash)
        self.params = {
            'chainId': client.network.chain_id,
            'nonce': int(tx_data.get('nonce')),
            'gasPrice': int(tx_data.get('gasPrice')),
            'gas': int(tx_data.get('gas')),
            'from': tx_data.get('from'),
            'to': tx_data.get('to'),
            'data': tx_data.get('input'),
            'value': int(tx_data.get('value'))
        }
        return self.params

    async def decode_input_data(
            self, client, contract: types.Contract
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Decode the input data of a sent transaction.

        Args:
            client (Client): the Client instance.
            contract (Contract): the contract instance whose ABI will be used to decode input data.

        Returns:
            Tuple[Optional[str], Optional[Dict[str, Any]]]: the function identifier and decoded input data
                of a sent transaction.

        """
        if not self.params or not self.params.get('data'):
            await self.parse_params(client=client)

        try:
            self.function_identifier, self.input_data = await Transactions.decode_input_data(
                client=client, contract=contract, input_data=self.params.get('data')
            )

        except:
            pass

        return self.function_identifier, self.input_data

    async def wait_for_receipt(
            self, client, timeout: Union[int, float] = 120, poll_latency: float = 0.1
    ) -> Dict[str, Any]:
        """
        Wait for the transaction receipt.

        Args:
            client (Client): the Client instance.
            timeout (Union[int, float]): the receipt waiting timeout. (120 sec)
            poll_latency (float): the poll latency. (0.1 sec)

        Returns:
            Dict[str, Any]: the transaction receipt.

        """
        self.receipt = dict(await client.w3.eth.wait_for_transaction_receipt(
            transaction_hash=self.hash, timeout=timeout, poll_latency=poll_latency
        ))
        return self.receipt

    async def cancel(
            self, client, gas_price: Optional[types.GasPrice] = None,
            gas_limit: Optional[types.GasLimit] = None
    ) -> bool:
        """
        Cancel the transaction.

        Args:
            client (Client): the Client instance.
            gas_price (Optional[GasPrice]): the gas price in GWei. (parsed from the network)
            gas_limit (Optional[GasLimit]): the gas limit in Wei. (parsed from the network)

        Returns:
            bool: True if the transaction was sent successfully.

        """
        if self.params and 'nonce' in self.params:
            if not gas_price:
                gas_price = (await Transactions.gas_price(w3=client.w3)).Wei

            elif isinstance(gas_price, (int, float)):
                gas_price = GWei(gas_price).Wei

            if gas_price < self.params.get('gasPrice') * 1.11:
                gas_price = int(self.params.get('gasPrice') * 1.11)

            tx_params = {
                'chainId': client.network.chain_id,
                'nonce': self.params.get('nonce'),
                'to': client.account.address,
                'value': 0
            }
            if client.network.tx_type == 2:
                tx_params['maxPriorityFeePerGas'] = (await client.transactions.max_priority_fee(w3=client.w3)).Wei
                tx_params['maxFeePerGas'] = gas_price + tx_params['maxPriorityFeePerGas']

            else:
                tx_params['gasPrice'] = gas_price

            if not gas_limit:
                gas_limit = await Transactions.estimate_gas(w3=client.w3, tx_params=tx_params)

            elif isinstance(gas_limit, int):
                gas_limit = Wei(gas_limit)

            tx_params['gas'] = gas_limit.Wei
            signed_tx = client.w3.eth.account.sign_transaction(
                transaction_dict=tx_params, private_key=client.account.key
            )
            tx_hash = await client.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            if tx_hash:
                self.hash = tx_hash
                self.params = tx_params.copy()
                return True

        return False

    async def speed_up(
            self, client, gas_price: Optional[types.GasPrice] = None, gas_limit: Optional[types.GasLimit] = None
    ) -> bool:
        """
        Speed up the transaction.

        Args:
            client (Client): the Client instance.
            gas_price (Optional[GasPrice]): the gas price in GWei. (parsed from the network * 1.5)
            gas_limit (Optional[GasLimit]): the gas limit in Wei. (parsed from the network)

        Returns:
            bool: True if the transaction was sent successfully.

        """
        if self.params and 'nonce' in self.params:
            if not gas_price:
                gas_price = int((await Transactions.gas_price(w3=client.w3)).Wei * 1.5)

            elif isinstance(gas_price, (int, float)):
                gas_price = GWei(gas_price).Wei

            tx_params = self.params.copy()
            if client.network.tx_type == 2:
                tx_params['maxPriorityFeePerGas'] = (await client.transactions.max_priority_fee(w3=client.w3)).Wei
                tx_params['maxFeePerGas'] = gas_price + tx_params['maxPriorityFeePerGas']

            else:
                tx_params['gasPrice'] = gas_price

            if not gas_limit:
                gas_limit = await Transactions.estimate_gas(w3=client.w3, tx_params=tx_params)

            elif isinstance(gas_limit, int):
                gas_limit = Wei(gas_limit)

            tx_params['gas'] = gas_limit.Wei
            signed_tx = client.w3.eth.account.sign_transaction(
                transaction_dict=tx_params, private_key=client.account.key
            )
            tx_hash = await client.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            if tx_hash:
                self.hash = tx_hash
                self.params = tx_params.copy()
                return True

        return False


class Transactions:
    """
    Class with functions related to transactions.

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

    @staticmethod
    async def current_gas_price(w3: Web3Async) -> Wei:
        print("This method will be deprecated in a future update. Use 'gas_price' instead.")
        return await Transactions.gas_price(w3=w3)

    @staticmethod
    async def gas_price(w3: Web3Async) -> Wei:
        """
        Get the current gas price.

        Args:
            w3 (Web3): the Web3 instance.

        Returns:
            Wei: the current gas price.

        """
        return Wei(await w3.eth.gas_price)

    @staticmethod
    async def max_priority_fee(w3: Web3Async) -> Wei:
        """
        Get the current max priority fee.

        Args:
            w3 (Web3): the Web3 instance.

        Returns:
            Wei: the current max priority fee.

        """
        return Wei(await w3.eth.max_priority_fee)

    @staticmethod
    async def estimate_gas(w3: Web3Async, tx_params: TxParams) -> Wei:
        """
        Get the estimate gas limit for a transaction with specified parameters.

        Args:
            w3 (Web3): the Web3 instance.
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Wei: the estimate gas.

        """
        return Wei(await w3.eth.estimate_gas(transaction=tx_params))

    @staticmethod
    async def decode_input_data(
            client, contract: types.Contract, input_data: Optional[str] = None, tx_hash: Optional[_Hash32] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Decode the input data of a sent transaction.

        Args:
            client (Client): the Client instance.
            contract (Contract): the contract address or instance whose ABI will be used to decode input data.
            input_data (Optional[str]): the raw input data. (None)
            tx_hash (Optional[_Hash32]): the transaction hash to parse input data. (None)

        Returns:
            Tuple[str, Dict[str, Any]]: the function identifier and decoded input data of a sent transaction.

        """
        if not input_data and not tx_hash:
            raise exceptions.TransactionException("Specify 'input_data' or 'tx_hash' argument values!")

        if not isinstance(contract, AsyncContract):
            contract = await client.contracts.get(contract_address=contract)

        if input_data:
            input_data = input_data

        else:
            input_data = (await client.w3.eth.get_transaction(transaction_hash=tx_hash)).get('input')

        function_instance, input_data = contract.decode_function_input(input_data)
        return function_instance.function_identifier, input_data

    async def auto_add_params(self, tx_params: TxParams) -> TxParams:
        """
        Add 'chainId', 'nonce', 'from', 'gasPrice' or 'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to
            transaction parameters if they are missing.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            TxParams: parameters of the transaction with added values.

        """
        if 'chainId' not in tx_params:
            tx_params['chainId'] = self.client.network.chain_id

        if 'nonce' not in tx_params:
            tx_params['nonce'] = await self.client.wallet.nonce()

        if 'from' not in tx_params:
            tx_params['from'] = self.client.account.address

        if 'gasPrice' not in tx_params and 'maxFeePerGas' not in tx_params:
            gas_price = (await self.gas_price(w3=self.client.w3)).Wei
            if self.client.network.tx_type == 2:
                tx_params['maxFeePerGas'] = gas_price

            else:
                tx_params['gasPrice'] = gas_price

        elif 'gasPrice' in tx_params and not int(tx_params['gasPrice']):
            tx_params['gasPrice'] = (await self.gas_price(w3=self.client.w3)).Wei

        if 'maxFeePerGas' in tx_params and 'maxPriorityFeePerGas' not in tx_params:
            tx_params['maxPriorityFeePerGas'] = (await self.max_priority_fee(w3=self.client.w3)).Wei
            tx_params['maxFeePerGas'] = tx_params['maxFeePerGas'] + tx_params['maxPriorityFeePerGas']

        if 'gas' not in tx_params or not int(tx_params['gas']):
            tx_params['gas'] = (await self.estimate_gas(w3=self.client.w3, tx_params=tx_params)).Wei

        return tx_params

    async def sign(self, tx_params: TxParams) -> SignedTransaction:
        print("This method will be deprecated in a future update. Use 'sign_transaction' instead.")
        return await self.sign_transaction(tx_params=tx_params)

    async def sign_transaction(self, tx_params: TxParams) -> SignedTransaction:
        """
        Sign a transaction.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            SignedTransaction: the signed transaction.

        """
        return self.client.w3.eth.account.sign_transaction(
            transaction_dict=tx_params, private_key=self.client.account.key
        )

    async def sign_message(self, message: str) -> SignedMessage:
        """
        Sign a message.

        Args:
            message (str): the message.

        Returns:
            str: the signed message.

        """
        return self.client.w3.eth.account.sign_message(
            encode_defunct(text=message), private_key=self.client.account.key
        )

    async def sign_and_send(self, tx_params: TxParams) -> Tx:
        """
        Sign and send a transaction. Additionally, add 'chainId', 'nonce', 'from', 'gasPrice' or
            'maxFeePerGas' + 'maxPriorityFeePerGas' and 'gas' parameters to transaction parameters if they are missing.

        Args:
            tx_params (TxParams): parameters of the transaction.

        Returns:
            Tx: the instance of the sent transaction.

        """
        await self.auto_add_params(tx_params=tx_params)
        signed_tx = await self.sign_transaction(tx_params)
        tx_hash = await self.client.w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
        return Tx(tx_hash=tx_hash, params=tx_params)

    @api_key_required
    async def history(self, address: Optional[str] = None, raw: bool = False) -> Union[RawTxHistory, TxHistory]:
        """
        Get the history instance containing list of normal, internal, ERC-20 and ERC-721 transactions of
            a specified address.

        Args:
            address (Optional[str]): the address to get the transaction list. (imported to client address)
            raw (bool): whether to return the raw data. (False)

        Returns:
            Union[RawTxHistory, TxHistory]: the history instance.

        """
        if not address:
            address = self.client.account.address

        account_api = self.client.network.api.functions.account
        coin_txs = (await account_api.txlist(address))['result']
        internal_txs = (await account_api.txlistinternal(address))['result']
        erc20_txs = (await account_api.tokentx(address))['result']
        erc721_txs = (await account_api.tokennfttx(address))['result']
        if raw:
            return RawTxHistory(
                address=address, coin_txs=coin_txs, internal_txs=internal_txs, erc20_txs=erc20_txs,
                erc721_txs=erc721_txs
            )

        return TxHistory(
            address=address, coin_txs=coin_txs, internal_txs=internal_txs, erc20_txs=erc20_txs, erc721_txs=erc721_txs
        )

    @api_key_required
    async def find_txs(
            self, contract: types.Contract, function_name: Optional[str] = '', address: Optional[types.Address] = None,
            after_timestamp: int = 0, before_timestamp: int = 999_999_999_999
    ) -> Dict[str, CoinTx]:
        """
        Find all transactions of interaction with the contract, in addition, you can filter transactions by
            the name of the contract function.

        Args:
            contract (Contract): the contract address or instance with which the interaction took place.
            function_name (Optional[str]): the function name for sorting. (any)
            address (Optional[Address]): the address to get the transaction list. (imported to client address)
            after_timestamp (int): after what time to filter transactions. (0)
            before_timestamp (int): before what time to filter transactions. (infinity)

        Returns:
            Dict[str, CoinTx]: transactions found.

        """
        contract_address, abi = await self.client.contracts.get_contract_attributes(contract)
        if not address:
            address = self.client.account.address

        txs = {}
        coin_txs = (await self.client.network.api.functions.account.txlist(address))['result']
        for tx in coin_txs:
            if (
                    after_timestamp < int(tx.get('timeStamp')) < before_timestamp and
                    tx.get('isError') == '0' and
                    tx.get('to') == contract_address.lower() and
                    function_name in tx.get('functionName')
            ):
                txs[tx.get('hash')] = CoinTx(data=tx)

        return txs

    async def approved_amount(
            self, token: types.Contract, spender: types.Contract, owner: Optional[types.Address] = None
    ) -> TokenAmount:
        """
        Get approved amount of token.

        Args:
            token (Contract): the contract address or instance of token.
            spender (Contract): the spender address, contract address or instance.
            owner (Optional[Address]): the owner address. (imported to client address)

        Returns:
            TokenAmount: the approved amount.

        """
        contract_address, abi = await self.client.contracts.get_contract_attributes(token)
        contract = await self.client.contracts.default_token(contract_address)
        spender, abi = await self.client.contracts.get_contract_attributes(spender)
        if not owner:
            owner = self.client.account.address

        return TokenAmount(
            amount=await contract.functions.allowance(checksum(owner), checksum(spender)).call(),
            decimals=await contract.functions.decimals().call(), wei=True
        )

    async def wait_for_receipt(
            self, tx_hash: Union[str, _Hash32], timeout: Union[int, float] = 120, poll_latency: float = 0.1
    ) -> Dict[str, Any]:
        """
        Wait for a transaction receipt.

        Args:
            tx_hash (Union[str, _Hash32]): the transaction hash.
            timeout (Union[int, float]): the receipt waiting timeout. (120)
            poll_latency (float): the poll latency. (0.1 sec)

        Returns:
            Dict[str, Any]: the transaction receipt.

        """
        return dict(await self.client.w3.eth.wait_for_transaction_receipt(
            transaction_hash=tx_hash, timeout=timeout, poll_latency=poll_latency
        ))

    async def send(
            self, token: types.Contract, recipient: types.Address, amount: types.Amount = 999_999_999_999_999,
            gas_price: Optional[types.GasPrice] = None, gas_limit: Optional[types.GasLimit] = None,
            nonce: Optional[int] = None, check_gas_price: bool = False, dry_run: bool = False
    ) -> Tx:
        """
        Send a coin or token.

        Args:
            token (Contract): the contract address or instance of token to send, use '' to send the coin.
            recipient (Address): the recipient address.
            amount (Amount): an amount to send. (entire balance)
            gas_price (Optional[GasPrice]): the gas price in GWei. (parsed from the network)
            gas_limit (Optional[GasLimit]): the gas limit in Wei. (parsed from the network)
            nonce (Optional[int]): a nonce of the sender address. (get it using the 'nonce' function)
            check_gas_price (bool): if True and the gas price is higher than that specified in the 'gas_price'
                argument, the 'GasPriceTooHigh' error will raise. (False)
            dry_run (bool): if True, it creates a parameter dictionary, but doesn't send the transaction. (False)

        Returns:
            Tx: the instance of the sent transaction.

        """
        if not token:
            contract = None

        else:
            contract_address, abi = await self.client.contracts.get_contract_attributes(token)
            contract = await self.client.contracts.default_token(contract_address)

        if isinstance(amount, (int, float)):
            if contract:
                amount = TokenAmount(amount=amount, decimals=await contract.functions.decimals().call())

            else:
                amount = Ether(amount=amount)

        amount = amount.Wei
        recipient = checksum(recipient)
        current_gas_price = await self.gas_price(w3=self.client.w3)
        if not gas_price:
            gas_price = current_gas_price

        elif gas_price:
            if isinstance(gas_price, (int, float)):
                gas_price = GWei(gas_price)

        if check_gas_price and current_gas_price > gas_price:
            raise exceptions.GasPriceTooHigh()

        if not nonce:
            nonce = await self.client.wallet.nonce()

        tx_params = {
            'chainId': self.client.network.chain_id,
            'nonce': nonce,
            'from': self.client.account.address
        }
        if self.client.network.tx_type == 2:
            tx_params['maxPriorityFeePerGas'] = (await self.client.transactions.max_priority_fee(w3=self.client.w3)).Wei
            tx_params['maxFeePerGas'] = gas_price.Wei + tx_params['maxPriorityFeePerGas']

        else:
            tx_params['gasPrice'] = gas_price.Wei

        if contract:
            balance = (await self.client.wallet.balance(token=contract)).Wei
            if balance < amount:
                amount = balance

            tx_params.update({
                'to': contract.address,
                'data': contract.encodeABI('transfer', args=TxArgs(recipient=recipient, amount=amount).tuple())
            })

        else:
            balance = (await self.client.wallet.balance()).Wei
            if balance < amount:
                amount = balance

            tx_params.update({
                'to': recipient,
                'value': amount
            })

        if not amount:
            raise exceptions.InsufficientBalance()

        if not gas_limit:
            gas_limit = await self.estimate_gas(w3=self.client.w3, tx_params=tx_params)

        elif isinstance(gas_limit, int):
            gas_limit = Wei(gas_limit)

        tx_params['gas'] = gas_limit.Wei
        if 'value' in tx_params:
            balance = (await self.client.wallet.balance()).Wei
            gas_price = tx_params.get('gasPrice') if 'gasPrice' in tx_params else tx_params.get('maxFeePerGas')
            available_to_send = balance - gas_price * tx_params.get('gas')
            if available_to_send < amount:
                tx_params['value'] = available_to_send

        if dry_run:
            return Tx(params=tx_params)

        return await self.sign_and_send(tx_params=tx_params)

    async def approve(
            self, token: types.Contract, spender: types.Address, amount: Optional[types.Amount] = None,
            gas_price: Optional[types.GasPrice] = None, gas_limit: Optional[types.GasLimit] = None,
            nonce: Optional[int] = None, check_gas_price: bool = False
    ) -> Tx:
        """
        Approve token spending for specified address.

        Args:
            token (Contract): the contract address or instance of token to approve.
            spender (Address): the spender address, contract address or instance.
            amount (Optional[Amount]): an amount to approve. (infinity)
            gas_price (Optional[GasPrice]): the gas price in GWei. (parsed from the network)
            gas_limit (Optional[GasLimit]): the gas limit in Wei. (parsed from the network)
            nonce (Optional[int]): a nonce of the sender address. (get it using the 'nonce' function)
            check_gas_price (bool): if True and the gas price is higher than that specified in the 'gas_price'
                argument, the 'GasPriceTooHigh' error will raise. (False)

        Returns:
            Tx: the instance of the sent transaction.

        """
        contract_address, abi = await self.client.contracts.get_contract_attributes(token)
        contract = await self.client.contracts.default_token(contract_address)
        if not amount:
            amount = CommonValues.InfinityInt

        elif isinstance(amount, (int, float)):
            amount = TokenAmount(amount=amount, decimals=await contract.functions.decimals().call()).Wei

        else:
            amount = amount.Wei

        spender = checksum(spender)
        current_gas_price = await self.gas_price(w3=self.client.w3)
        if not gas_price:
            gas_price = current_gas_price

        elif gas_price:
            if isinstance(gas_price, (int, float)):
                gas_price = GWei(gas_price)

        if check_gas_price and current_gas_price > gas_price:
            raise exceptions.GasPriceTooHigh()

        if not nonce:
            nonce = await self.client.wallet.nonce()

        tx_params = {
            'chainId': self.client.network.chain_id,
            'nonce': nonce,
            'from': self.client.account.address,
            'to': contract.address,
            'data': contract.encodeABI('approve', args=TxArgs(spender=spender, amount=amount).tuple())
        }
        if self.client.network.tx_type == 2:
            tx_params['maxPriorityFeePerGas'] = (await self.client.transactions.max_priority_fee(w3=self.client.w3)).Wei
            tx_params['maxFeePerGas'] = gas_price.Wei + tx_params['maxPriorityFeePerGas']

        else:
            tx_params['gasPrice'] = gas_price.Wei

        if not gas_limit:
            gas_limit = await self.estimate_gas(w3=self.client.w3, tx_params=tx_params)

        elif isinstance(gas_limit, int):
            gas_limit = Wei(gas_limit)

        tx_params['gas'] = gas_limit.Wei
        return await self.sign_and_send(tx_params=tx_params)
