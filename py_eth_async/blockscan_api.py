from typing import Optional, Union, List, Dict, Any

from fake_useragent import UserAgent
from pretty_utils.miscellaneous.http import aiohttp_params

from py_eth_async import exceptions
from py_eth_async.utils import async_get


class Tag:
    """
    An instance with tag values.
    """
    Earliest: str = 'earliest'
    Pending: str = 'pending'
    Latest: str = 'latest'


class Sort:
    """
    An instance with sort values.
    """
    Asc: str = 'asc'
    Desc: str = 'desc'


class BlockType:
    """
    An instance with block type values.
    """
    Blocks: str = 'blocks'
    Uncles: str = 'uncles'


class Closest:
    """
    An instance with closest values.
    """
    Before: str = 'before'
    After: str = 'after'


class ClientType:
    """
    An instance with client type values.
    """
    Geth: str = 'geth'
    Parity: str = 'parity'


class SyncMode:
    """
    An instance with sync mode values.
    """
    Default: str = 'default'
    Archive: str = 'archive'


class APIFunctions:
    """
    Class with functions related to Blockscan API.

    Attributes:
        key (str): an API key.
        url (str): an API entrypoint URL.
        headers (Dict[str, Any]): a headers for requests.
        account (Account): functions related to 'account' API module.
        contract (Contract): functions related to 'contract' API module.
        transaction (Transaction): functions related to 'transaction' API module.
        block (Block): functions related to 'block' API module.
        logs (Logs): functions related to 'logs' API module.
        token (Token): functions related to 'token' API module.
        gastracker (Gastracker): functions related to 'gastracker' API module.
        stats (Stats): functions related to 'stats' API module.

    """

    def __init__(self, key: str, url: str) -> None:
        """
        Initialize the class.

        Args:
            key (str): an API key.
            url (str): an API entrypoint URL.

        """
        self.key = key
        self.url = url
        self.headers = {'content-type': 'application/json', 'user-agent': UserAgent().chrome}
        self.account = Account(self.key, self.url, self.headers)
        self.contract = Contract(self.key, self.url, self.headers)
        self.transaction = Transaction(self.key, self.url, self.headers)
        self.block = Block(self.key, self.url, self.headers)
        self.logs = Logs(self.key, self.url, self.headers)
        self.token = Token(self.key, self.url, self.headers)
        self.gastracker = Gastracker(self.key, self.url, self.headers)
        self.stats = Stats(self.key, self.url, self.headers)


class Module:
    """
    Class with functions related to some API module.

    Attributes:
        key (str): an API key.
        url (str): an API entrypoint URL.
        headers (Dict[str, Any]): a headers for requests.
        module (str): a module name.

    """
    key: str
    url: str
    headers: Dict[str, Any]
    module: str

    def __init__(self, key: str, url: str, headers: Dict[str, Any]) -> None:
        """
        Initialize the class.

        Args:
            key (str): an API key.
            url (str): an API entrypoint URL.
            headers (Dict[str, Any]): a headers for requests.

        """
        self.key = key
        self.url = url
        self.headers = headers


class Account(Module):
    """
    Class with functions related to 'account' API module.
    """
    module: str = 'account'

    async def balance(self, address: str, tag: Union[str, Tag] = Tag.Latest) -> Dict[str, Any]:
        """
        Return the Ether balance of a given address.

        https://docs.etherscan.io/api-endpoints/accounts#get-ether-balance-for-a-single-address

        Args:
            address (str): the address to check for balance
            tag (Union[str, Tag]): the pre-defined block parameter, either "earliest", "pending" or "latest". ("latest")

        Returns:
            Dict[str, Any]: the dictionary with the Ether balance of the address in wei.

        """
        action = 'balance'
        if tag not in ('earliest', 'pending', 'latest'):
            raise exceptions.APIException('"tag" parameter have to be either "earliest", "pending" or "latest"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'tag': tag
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def balancemulti(self, addresses: List[str], tag: Union[str, Tag] = Tag.Latest) -> Dict[str, Any]:
        """
        Return the balance of the accounts from a list of addresses.

        https://docs.etherscan.io/api-endpoints/accounts#get-ether-balance-for-multiple-addresses-in-a-single-call

        Args:
            addresses (List[str]): the list of up to 20 addresses to check for balance.
            tag (Union[str, Tag]): the pre-defined block parameter, either "earliest", "pending" or "latest". ("latest")

        Returns:
            Dict[str, Any]: the dictionary with the Ether balances for the addresses in wei.

        """
        action = 'balancemulti'
        if tag not in ('earliest', 'pending', 'latest'):
            raise exceptions.APIException('"tag" parameter have to be either "earliest", "pending" or "latest"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': addresses,
            'tag': tag
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def txlist(
            self, address: str, startblock: Optional[int] = None, endblock: Optional[int] = None,
            page: Optional[int] = None, offset: Optional[int] = None, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the list of transactions performed by an address, with optional pagination.

        https://docs.etherscan.io/api-endpoints/accounts#get-a-list-of-normal-transactions-by-address

        Args:
            address (str): the address to get the transaction list.
            startblock (Optional[int]): the block number to start searching for transactions.
            endblock (Optional[int]): the block number to stop searching for transactions.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the list of transactions performed by the address.

        """
        action = 'txlist'
        if sort not in ('asc', 'desc'):
            raise exceptions.APIException('"sort" parameter have to be either "asc" or "desc"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'sort': sort,
            'startblock': startblock,
            'endblock': endblock,
            'page': page,
            'offset': offset
        }

        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def txlistinternal(
            self, address: Optional[str] = None, txhash: Optional[str] = None, startblock: Optional[int] = None,
            endblock: Optional[int] = None, page: Optional[int] = None, offset: Optional[int] = None,
            sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the list of internal transactions performed by an address, with optional pagination.

        https://docs.etherscan.io/api-endpoints/accounts#get-a-list-of-internal-transactions-by-address

        Args:
            address (Optional[str]): the address to get the transaction list.
            txhash (Optional[str]): the transaction hash to check for internal transactions.
            startblock (Optional[int]): the block number to start searching for transactions.
            endblock (Optional[int]): the block number to stop searching for transactions.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the list of internal transactions performed by the address.

        """
        action = 'txlistinternal'
        if sort not in ('asc', 'desc'):
            raise exceptions.APIException('"sort" parameter have to be either "asc" or "desc"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key
        }

        if not address and not txhash:
            if not startblock and endblock:
                raise exceptions.APIException('Specify "startblock" an "endblock" parameters')

            params['startblock'] = startblock
            params['endblock'] = endblock
            params['sort'] = sort
            params['page'] = page
            params['offset'] = offset

        elif txhash:
            params['txhash'] = txhash

        else:
            params['address'] = address
            params['sort'] = sort
            params['startblock'] = startblock
            params['endblock'] = endblock
            params['page'] = page
            params['offset'] = offset

        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def tokentx(
            self, address: str, contractaddress: Optional[str] = None, startblock: Optional[int] = None,
            endblock: Optional[int] = None, page: Optional[int] = None, offset: Optional[int] = None,
            sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the list of ERC-20 tokens transferred by an address, with optional filtering by token contract.

        https://docs.etherscan.io/api-endpoints/accounts#get-a-list-of-erc20-token-transfer-events-by-address

        Args:
            address (str): the address to get the transaction list.
            contractaddress (Optional[str]): the token contract address to check for transactions.
            startblock (Optional[int]): the block number to start searching for transactions.
            endblock (Optional[int]): the block number to stop searching for transactions.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the list of ERC-20 token transactions performed by the address.

        """
        action = 'tokentx'
        if sort not in ('asc', 'desc'):
            raise exceptions.APIException('"sort" parameter have to be either "asc" or "desc"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'sort': sort,
            'contractaddress': contractaddress,
            'startblock': startblock,
            'endblock': endblock,
            'page': page,
            'offset': offset
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def tokennfttx(
            self, address: str, contractaddress: Optional[str] = None, startblock: Optional[int] = None,
            endblock: Optional[int] = None, page: Optional[int] = None, offset: Optional[int] = None,
            sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the list of ERC-721 (NFT) tokens transferred by an address, with optional filtering by token contract.

        https://docs.etherscan.io/api-endpoints/accounts#get-a-list-of-erc721-token-transfer-events-by-address

        Args:
            address (str): the address to get the transaction list.
            contractaddress (Optional[str]): the token contract address to check for transactions.
            startblock (Optional[int]): the block number to start searching for transactions.
            endblock (Optional[int]): the block number to stop searching for transactions.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the list of ERC-721 token transactions performed by the address.

        """
        action = 'tokennfttx'
        if sort not in ('asc', 'desc'):
            raise exceptions.APIException('"sort" parameter have to be either "asc" or "desc"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'sort': sort,
            'contractaddress': contractaddress,
            'startblock': startblock,
            'endblock': endblock,
            'page': page,
            'offset': offset
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def token1155tx(
            self, address: str, contractaddress: Optional[str] = None, startblock: Optional[int] = None,
            endblock: Optional[int] = None, page: Optional[int] = None, offset: Optional[int] = None,
            sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the list of ERC-1155 (Multi Token Standard) tokens transferred by an address, with optional filtering by token contract.

        https://docs.etherscan.io/api-endpoints/accounts#get-a-list-of-erc1155-token-transfer-events-by-address

        Args:
            address (str): the address to get the transaction list.
            contractaddress (Optional[str]): the token contract address to check for transactions.
            startblock (Optional[int]): the block number to start searching for transactions.
            endblock (Optional[int]): the block number to stop searching for transactions.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the list of ERC-1155 token transactions performed by the address.

        """
        action = 'token1155tx'
        if sort not in ('asc', 'desc'):
            raise exceptions.APIException('"sort" parameter have to be either "asc" or "desc"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'sort': sort,
            'contractaddress': contractaddress,
            'startblock': startblock,
            'endblock': endblock,
            'page': page,
            'offset': offset
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def getminedblocks(
            self, address: str, blocktype: Union[str, BlockType] = BlockType.Blocks, page: Optional[int] = None,
            offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return the list of blocks mined by an address.

        https://docs.etherscan.io/api-endpoints/accounts#get-list-of-blocks-mined-by-address

        Args:
            address (str): the address to check for mined blocks.
            blocktype (Union[str, BlockType]): the pre-defined block type, either "blocks" for canonical blocks
                or "uncles" for uncle blocks only. ("blocks")
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.

        Returns:
            Dict[str, Any]: the dictionary with the list of mined blocks by the address.

        """
        action = 'getminedblocks'
        if blocktype not in ('blocks', 'uncles'):
            raise exceptions.APIException('"blocktype" parameter have to be either "blocks" or "uncles"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'blocktype': blocktype,
            'page': page,
            'offset': offset
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def balancehistory(self, address: str, blockno: int) -> Dict[str, Any]:
        """
        Return the balance of an address at a certain block height. (PRO)

        https://docs.etherscan.io/api-endpoints/accounts#get-historical-ether-balance-for-a-single-address-by-blockno

        Args:
            address (str): the address to check for balance.
            blockno (int): the block number to check balance.

        Returns:
            Dict[str, Any]: the dictionary with the Ether balance of the address in wei.

        """
        action = 'balancehistory'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'blockno': blockno
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def tokenbalance(self, contractaddress: str, address: str) -> Dict[str, Any]:
        """
        Return the current balance of an ERC-20 token of an address.

        https://docs.etherscan.io/api-endpoints/tokens#get-erc20-token-account-balance-for-tokencontractaddress

        Args:
            contractaddress (str): the contract address of the ERC-20 token.
            address (str): the address to check for token balance.

        Returns:
            Dict[str, Any]: the dictionary with the token balance of the address.

        """
        action = 'tokenbalance'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'contractaddress': contractaddress,
            'address': address
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def tokenbalancehistory(self, contractaddress: str, address: str, blockno: int) -> Dict[str, Any]:
        """
        Return the balance of an ERC-20 token of an address at a certain block height. (PRO)

        https://docs.etherscan.io/api-endpoints/tokens#get-historical-erc20-token-account-balance-for-tokencontractaddress-by-blockno

        Args:
            contractaddress (str): the contract address of the ERC-20 token.
            address (str): the address to check for balance.
            blockno (str): the block number to check balance.

        Returns:
            Dict[str, Any]: the dictionary with the ERC-20 token balance of the address.

        """
        action = 'tokenbalancehistory'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'contractaddress': contractaddress,
            'address': address,
            'blockno': blockno
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def addresstokenbalance(
            self, address: str, page: Optional[int] = None, offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return the ERC-20 tokens and amount held by an address. (PRO)

        https://docs.etherscan.io/api-endpoints/tokens#get-address-erc20-token-holding

        Args:
            address (str): the address to check for balance.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.

        Returns:
            Dict[str, Any]: the dictionary with the ERC-20 tokens and amount held by an address.

        """
        action = 'addresstokenbalance'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'page': page,
            'offset': offset
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def addresstokennftbalance(
            self, address: str, page: Optional[int] = None, offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return the ERC-721 tokens and amount held by an address. (PRO)

        https://docs.etherscan.io/api-endpoints/tokens#get-address-erc721-token-holding

        Args:
            address (str): the address to check for balance.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.

        Returns:
            Dict[str, Any]: the dictionary with the ERC-721 tokens and amount held by an address..

        """
        action = 'addresstokennftbalance'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'page': page,
            'offset': offset
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def addresstokennftinventory(
            self, address: str, page: Optional[int] = None, offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return the ERC-721 token inventory of an address, filtered by contract address. (PRO)

        https://docs.etherscan.io/api-endpoints/tokens#get-address-erc721-token-inventory-by-contract-address

        Args:
            address (str): the address to check for balance.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.

        Returns:
            Dict[str, Any]: the dictionary with the ERC-721 tokens and amount held by an address..

        """
        action = 'addresstokennftinventory'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'page': page,
            'offset': offset
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)


class Contract(Module):
    """
    Class with functions related to 'contract' API module.
    """
    module: str = 'contract'

    async def getabi(self, address: str) -> Dict[str, Any]:
        """
        Return the Contract Application Binary Interface (ABI) of a verified smart contract.

        https://docs.etherscan.io/api-endpoints/contracts#get-contract-abi-for-verified-contract-source-codes

        Args:
            address (str): the contract address that has a verified source code.

        Returns:
            Dict[str, Any]: the dictionary with the contract ABI.

        """
        action = 'getabi'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def getsourcecode(self, address: str) -> Dict[str, Any]:
        """
        Return the Solidity source code of a verified smart contract.

        https://docs.etherscan.io/api-endpoints/contracts#get-contract-source-code-for-verified-contract-source-codes

        Args:
            address (str): the contract address that has a verified source code.

        Returns:
            Dict[str, Any]: the dictionary with the contract source code.

        """
        action = 'getsourcecode'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def getcontractcreation(self, addresses: List[str]) -> Dict[str, Any]:
        """
        Return a contract's deployer address and transaction hash it was created, up to 5 at a time.

        https://docs.etherscan.io/api-endpoints/contracts#get-contract-creator-and-creation-tx-hash

        Args:
            addresses (str): the contract address, up to 5 at a time.

        Returns:
            Dict[str, Any]: the dictionary with a contract's deployer address and transaction hash it was created.

        """
        action = 'getcontractcreation'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': addresses
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)


class Transaction(Module):
    """
    Class with functions related to 'transaction' API module.
    """
    module: str = 'transaction'

    async def getstatus(self, txhash: str) -> Dict[str, Any]:
        """
        Return the status code of a contract execution.

        https://docs.etherscan.io/api-endpoints/stats#check-contract-execution-status

        Args:
            txhash (str): the transaction hash to check the execution status.

        Returns:
            Dict[str, Any]: the dictionary with the contract status code.

        """
        action = 'getstatus'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'txhash': txhash
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def gettxreceiptstatus(self, txhash: str) -> Dict[str, Any]:
        """
        Return the status code of a transaction execution.

        https://docs.etherscan.io/api-endpoints/stats#check-transaction-receipt-status

        Args:
            txhash (str): the transaction hash to check the execution status.

        Returns:
            Dict[str, Any]: the dictionary with the transaction status code.

        """
        action = 'gettxreceiptstatus'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'txhash': txhash
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)


class Block(Module):
    """
    Class with functions related to 'block' API module.
    """
    module: str = 'block'

    async def getblockreward(self, blockno: int) -> Dict[str, Any]:
        """
        Return the block reward and 'Uncle' block rewards.

        https://docs.etherscan.io/api-endpoints/blocks#get-block-and-uncle-rewards-by-blockno

        Args:
            blockno (int): the block number to check block rewards.

        Returns:
            Dict[str, Any]: the dictionary with the block rewards.

        """
        action = 'getblockreward'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'blockno': blockno
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def getblockcountdown(self, blockno: int) -> Dict[str, Any]:
        """
        Return the estimated time remaining, in seconds, until a certain block is mined.

        https://docs.etherscan.io/api-endpoints/blocks#get-estimated-block-countdown-time-by-blockno

        Args:
            blockno (int): the block number to estimate time remaining to be mined.

        Returns:
            Dict[str, Any]: the dictionary with the estimated time remaining until a certain block is mined.

        """
        action = 'getblockcountdown'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'blockno': blockno
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def getblocknobytime(self, timestamp: int, closest: Union[str, Closest] = Closest.Before) -> Dict[str, Any]:
        """
        Return the block number that was mined at a certain timestamp.

        https://docs.etherscan.io/api-endpoints/blocks#get-block-number-by-timestamp

        Args:
            timestamp (str): the Unix timestamp in seconds.
            closest (Union[str, Closest]): the closest available block to the provided timestamp,
                either "before" or "after". ("before")

        Returns:
            Dict[str, Any]: the dictionary with the block number that was mined at a certain timestamp.

        """
        action = 'getblocknobytime'
        if closest not in ('before', 'after'):
            raise exceptions.APIException('"closest" parameter have to be either "before" or "after"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'timestamp': timestamp,
            'closest': closest
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)


class Logs(Module):
    """
    Class with functions related to 'logs' API module.
    """
    module: str = 'log'

    async def getLogs(
            self, address: Optional[str], fromBlock: Optional[int], toBlock: Optional[int], page: Optional[int] = None,
            offset: Optional[int] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Return the event logs from an address, with optional filtering by block range.

        https://docs.etherscan.io/api-endpoints/logs#get-event-logs-by-address

        Args:
            address (Optional[str]): the address to get the transaction list.
            fromBlock (Optional[int]): the block number to start searching for logs.
            toBlock (Optional[int]): the block number to stop searching for logs.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.
            **kwargs: the topic numbers to search for and the topic operator when multiple topic combinations are used.

        Returns:
            Dict[str, Any]: the dictionary with the list of transactions performed by the address.

        """
        action = 'getLogs'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'address': address,
            'fromBlock': fromBlock,
            'toBlock': toBlock,
            'page': page,
            'offset': offset
        }
        for key, value in kwargs.items():
            params[key] = value

        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)


class Token(Module):
    """
    Class with functions related to 'token' API module.
    """
    module: str = 'token'

    async def tokenholderlist(
            self, contractaddress: str, page: Optional[int] = None, offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Return project information and social media links of an ERC20/ERC721/ERC1155 token. (PRO)

        https://docs.etherscan.io/api-endpoints/tokens#get-token-holder-list-by-contract-address

        Args:
            contractaddress (str): the contract address of the ERC-20 token.
            page (Optional[int]): the page number, if pagination is enabled.
            offset (Optional[int]): the number of transactions displayed per page.

        Returns:
            Dict[str, Any]: the dictionary with the project information and social media links of
                an ERC20/ERC721/ERC1155 token.

        """
        action = 'tokenholderlist'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'contractaddress': contractaddress,
            'page': page,
            'offset': offset
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def tokeninfo(self, contractaddress: str) -> Dict[str, Any]:
        """
        Return project information and social media links of an ERC20/ERC721/ERC1155 token. (PRO)

        https://docs.etherscan.io/api-endpoints/tokens#get-token-info-by-contractaddress

        Args:
            contractaddress (str): the contract address of the ERC-20 token.

        Returns:
            Dict[str, Any]: the dictionary with the project information and social media links of
                an ERC20/ERC721/ERC1155 token.

        """
        action = 'tokeninfo'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'contractaddress': contractaddress
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)


class Gastracker(Module):
    """
    Class with functions related to 'gastracker' API module.
    """
    module: str = 'gastracker'

    async def gasestimate(self, gasprice: int) -> Dict[str, Any]:
        """
        Return the estimated time, in seconds, for a transaction to be confirmed on the blockchain.

        https://docs.etherscan.io/api-endpoints/gas-tracker#get-estimation-of-confirmation-time

        Args:
            gasprice (int): the price paid per unit of gas, in wei.

        Returns:
            Dict[str, Any]: the dictionary with the estimated time, in seconds, for a transaction to be confirmed
                on the blockchain.

        """
        action = 'gasestimate'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'gasprice': gasprice
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def gasoracle(self) -> Dict[str, Any]:
        """
        Return the current Safe, Proposed and Fast gas prices.

        https://docs.etherscan.io/api-endpoints/gas-tracker#get-gas-oracle

        Returns:
            Dict[str, Any]: the dictionary with the current Safe, Proposed and Fast gas prices.

        """
        action = 'gasoracle'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)


class Stats(Module):
    """
    Class with functions related to 'stats' API module.
    """
    module: str = 'stats'

    async def ethsupply(self) -> Dict[str, Any]:
        """
        Return the current amount of Ether in circulation excluding ETH2 Staking rewards and EIP1559 burnt fees.

        https://docs.etherscan.io/api-endpoints/stats-1#get-total-supply-of-ether

        Returns:
            Dict[str, Any]: the dictionary with the current amount of Ether.

        """
        action = 'ethsupply'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def ethsupply2(self) -> Dict[str, Any]:
        """
        Return the current amount of Ether in circulation, ETH2 Staking rewards and EIP1559 burnt fees statistics.

        https://docs.etherscan.io/api-endpoints/stats-1#get-total-supply-of-ether-2

        Returns:
            Dict[str, Any]: the dictionary with the current amount of Ether.

        """
        action = 'ethsupply2'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def ethprice(self) -> Dict[str, Any]:
        """
        Return the latest price of 1 ETH.

        https://docs.etherscan.io/api-endpoints/stats-1#get-ether-last-price

        Returns:
            Dict[str, Any]: the dictionary with the latest Ether price.

        """
        action = 'ethprice'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def chainsize(
            self, startdate: str, enddate: str, clienttype: Union[str, ClientType] = ClientType.Geth,
            syncmode: Union[str, SyncMode] = SyncMode.Default, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the size of the Ethereum blockchain, in bytes, over a date range.

        https://docs.etherscan.io/api-endpoints/stats-1#get-ethereum-nodes-size

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (int): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            clienttype (Union[str, ClientType]): the Ethereum node client to use, either "geth" or "parity". ("geth")
            syncmode (Union[str, SyncMode]): the type of node to run, either "default" or "archive". ("default")
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the list of transactions performed by the address.

        """
        action = 'chainsize'
        if clienttype not in ('geth', 'parity'):
            raise exceptions.APIException('"clienttype" parameter have to be either "geth" or "parity"')

        if syncmode not in ('default', 'archive'):
            raise exceptions.APIException('"syncmode" parameter have to be either "default" or "archive"')

        if sort not in ('asc', 'desc'):
            raise exceptions.APIException('"sort" parameter have to be either "asc" or "desc"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'startdate': startdate,
            'enddate': enddate,
            'clienttype': clienttype,
            'syncmode': syncmode,
            'sort': sort
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def nodecount(self) -> Dict[str, Any]:
        """
        Return the total number of discoverable Ethereum nodes.

        https://docs.etherscan.io/api-endpoints/stats-1#get-total-nodes-count

        Returns:
            Dict[str, Any]: the dictionary with the total number of discoverable Ethereum nodes.

        """
        action = 'nodecount'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def general(
            self, action: str, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Function for sending similar requests.

        Args:
            action (str): the action name.
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the data.

        """
        if sort not in ('asc', 'desc'):
            raise exceptions.APIException('"sort" parameter have to be either "asc" or "desc"')

        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'startdate': startdate,
            'enddate': enddate,
            'sort': sort
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def dailytxnfee(self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc) -> Dict[str, Any]:
        """
        Return the amount of transaction fees paid to miners per day. (PRO)

        https://docs.etherscan.io/api-endpoints/stats-1#get-daily-network-transaction-fee

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the amount of transaction fees paid to miners per day.

        """
        return await self.general(action='dailytxnfee', startdate=startdate, enddate=enddate, sort=sort)

    async def dailynewaddress(self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc) -> Dict[str, Any]:
        """
        Return the number of new Ethereum addresses created per day. (PRO)

        https://docs.etherscan.io/api-endpoints/stats-1#get-daily-new-address-count

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the number of new Ethereum addresses created per day.

        """
        return await self.general(action='dailynewaddress', startdate=startdate, enddate=enddate, sort=sort)

    async def dailynetutilization(
            self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the daily average gas used over gas limit, in percentage. (PRO)

        https://docs.etherscan.io/api-endpoints/stats-1#get-daily-new-address-count

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the daily average gas used over gas limit.

        """
        return await self.general(action='dailynetutilization', startdate=startdate, enddate=enddate, sort=sort)

    async def dailyavghashrate(self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc) -> Dict[str, Any]:
        """
        Return the historical measure of processing power of the Ethereum network. (PRO)

        https://docs.etherscan.io/api-endpoints/stats-1#get-daily-average-network-hash-rate

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the historical measure of processing power.

        """
        return await self.general(action='dailyavghashrate', startdate=startdate, enddate=enddate, sort=sort)

    async def dailytx(self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc) -> Dict[str, Any]:
        """
        Return the number of transactions performed on the Ethereum blockchain per day. (PRO)

        https://docs.etherscan.io/api-endpoints/stats-1#get-daily-transaction-count

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the number of transactions performed per day.

        """
        return await self.general(action='dailytx', startdate=startdate, enddate=enddate, sort=sort)

    async def dailyavgnetdifficulty(
            self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the historical mining difficulty of the Ethereum network. (PRO)

        https://docs.etherscan.io/api-endpoints/stats-1#get-daily-average-network-difficulty

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the historical mining difficulty.

        """
        return await self.general(action='dailyavgnetdifficulty', startdate=startdate, enddate=enddate, sort=sort)

    async def ethdailymarketcap(
            self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the historical Ether daily market capitalization. (PRO)

        https://docs.etherscan.io/api-endpoints/stats-1#get-ether-historical-daily-market-cap

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the historical Ether daily market capitalization.

        """
        return await self.general(action='ethdailymarketcap', startdate=startdate, enddate=enddate, sort=sort)

    async def ethdailyprice(self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc) -> Dict[str, Any]:
        """
        Return the historical price of 1 ETH. (PRO)

        https://docs.etherscan.io/api-endpoints/stats-1#get-ether-historical-price

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the historical price 1 ETH.

        """
        return await self.general(action='ethdailyprice', startdate=startdate, enddate=enddate, sort=sort)

    async def dailyavgblocksize(
            self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the daily average block size within a date range. (PRO)

        https://docs.etherscan.io/api-endpoints/blocks#get-daily-average-block-size

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the daily average block size within a date range.

        """
        return await self.general(action='dailyavgblocksize', startdate=startdate, enddate=enddate, sort=sort)

    async def dailyblkcount(self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc) -> Dict[str, Any]:
        """
        Return the number of blocks mined daily and the amount of block rewards. (PRO)

        https://docs.etherscan.io/api-endpoints/blocks#get-daily-block-count-and-rewards

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the number of blocks mined daily and the amount of block rewards.

        """
        return await self.general(action='dailyblkcount', startdate=startdate, enddate=enddate, sort=sort)

    async def dailyblockrewards(
            self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the amount of block rewards distributed to miners daily. (PRO)

        https://docs.etherscan.io/api-endpoints/blocks#get-daily-block-rewards

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the amount of block rewards distributed to miners daily.

        """
        return await self.general(action='dailyblockrewards', startdate=startdate, enddate=enddate, sort=sort)

    async def dailyavgblocktime(
            self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the daily average of time needed for a block to be successfully mined. (PRO)

        https://docs.etherscan.io/api-endpoints/blocks#get-daily-average-time-for-a-block-to-be-included-in-the-ethereum-blockchain

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the daily average of time needed for a block to be successfully mined.

        """
        return await self.general(action='dailyavgblocktime', startdate=startdate, enddate=enddate, sort=sort)

    async def dailyuncleblkcount(
            self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc
    ) -> Dict[str, Any]:
        """
        Return the number of 'Uncle' blocks mined daily and the amount of 'Uncle' block rewards. (PRO)

        https://docs.etherscan.io/api-endpoints/blocks#get-daily-uncle-block-count-and-rewards

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the number of 'Uncle' blocks mined daily and the amount of
                'Uncle' block rewards.

        """
        return await self.general(action='dailyuncleblkcount', startdate=startdate, enddate=enddate, sort=sort)

    async def dailyavggaslimit(self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc) -> Dict[str, Any]:
        """
        Return the historical daily average gas limit of the Ethereum network. (PRO)

        https://docs.etherscan.io/api-endpoints/gas-tracker#get-daily-average-gas-limit

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the historical daily average gas limit of the Ethereum network.

        """
        return await self.general(action='dailyavggaslimit', startdate=startdate, enddate=enddate, sort=sort)

    async def dailygasused(self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc) -> Dict[str, Any]:
        """
        Return the total amount of gas used daily for transctions on the Ethereum network. (PRO)

        https://docs.etherscan.io/api-endpoints/gas-tracker#get-ethereum-daily-total-gas-used

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the total amount of gas used daily for transctions on the Ethereum
                network.

        """
        return await self.general(action='dailygasused', startdate=startdate, enddate=enddate, sort=sort)

    async def dailyavggasprice(self, startdate: str, enddate: str, sort: Union[str, Sort] = Sort.Asc) -> Dict[str, Any]:
        """
        Return the daily average gas price used on the Ethereum network. (PRO)

        https://docs.etherscan.io/api-endpoints/gas-tracker#get-daily-average-gas-price

        Args:
            startdate (str): the starting date in yyyy-MM-dd format, eg. 2019-02-01.
            enddate (str): the ending date in yyyy-MM-dd format, eg. 2019-02-28.
            sort (Union[str, Sort]): the sorting preference, use "asc" to sort by ascending and "desc" to sort
                by descending. ("asc")

        Returns:
            Dict[str, Any]: the dictionary with the daily average gas price used on the Ethereum network.

        """
        return await self.general(action='dailyavggasprice', startdate=startdate, enddate=enddate, sort=sort)

    async def tokensupply(self, contractaddress: str) -> Dict[str, Any]:
        """
        Return the current amount of an ERC-20 token in circulation.

        https://docs.etherscan.io/api-endpoints/tokens#get-erc20-token-totalsupply-by-contractaddress

        Args:
            contractaddress (str): the contract address of the ERC-20 token.

        Returns:
            Dict[str, Any]: the dictionary with the current amount of an ERC-20 token in circulation.

        """
        action = 'tokensupply'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'contractaddress': contractaddress
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)

    async def tokensupplyhistory(self, contractaddress: str, blockno: int) -> Dict[str, Any]:
        """
        Return the amount of an ERC-20 token in circulation at a certain block height. (PRO)

        https://docs.etherscan.io/api-endpoints/tokens#get-historical-erc20-token-totalsupply-by-contractaddress-and-blockno

        Args:
            contractaddress (str): the contract address of the ERC-20 token.
            blockno (int): the block number to check total supply.

        Returns:
            Dict[str, Any]: the dictionary with the amount of an ERC-20 token in circulation at a certain block height.

        """
        action = 'tokensupplyhistory'
        params = {
            'module': self.module,
            'action': action,
            'apikey': self.key,
            'contractaddress': contractaddress,
            'blockno': blockno
        }
        return await async_get(self.url, params=aiohttp_params(params), headers=self.headers)
