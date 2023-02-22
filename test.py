import asyncio
import os
import random

from web3.contract import AsyncContract

from py_eth_async.client import Client
from py_eth_async.data.models import Networks, Wei, Ether, GWei, TokenAmount, Network, TxArgs
from py_eth_async.transactions import Tx
from py_eth_async.utils import get_coin_symbol


class Account:
    @staticmethod
    async def generate_wallets(n: int = 2):
        """Generate wallets."""
        print('\n--- generate_wallets ---')
        for i in range(n):
            client = Client()
            print(f'{client.account.address} {client.account.key.hex()}')

    @staticmethod
    async def show_coin_balance():
        """Show balance in coin."""
        print('\n--- show_coin_balance ---')
        client = Client(private_key=private_key)
        address = '0xf5de760f2e916647fd766B4AD9E85ff943cE3A2b'
        coin_symbol = await get_coin_symbol(chain_id=client.network.chain_id)
        print(f'''Your ({client.account.address}) balance: {(await client.wallet.balance()).Ether} {coin_symbol}
{address} balance: {(await client.wallet.balance(address=address)).Ether} {coin_symbol}''')

    @staticmethod
    async def show_token_balance():
        """Show balance in token."""
        print('\n--- show_token_balance ---')
        client = Client(private_key=private_key)
        address = '0xe4C004883BE7EB6e059005aAf6A34B45722fE3c9'
        contract = await client.contracts.get(contract_address='0x326c977e6efc84e512bb9c30f76e30c160ed06fb')
        coin_symbol = await contract.functions.symbol().call()
        print(
            f'''Your ({client.account.address}) balance: {(await client.wallet.balance(token=contract)).Ether} {coin_symbol}
{address} balance: {(await client.wallet.balance(token='0x326c977e6efc84e512bb9c30f76e30c160ed06fb',
                                                 address=address)).Ether} {coin_symbol}''')


class Contracts:
    @staticmethod
    async def get_abi():
        """Get a contract ABI."""
        print('\n--- get_abi ---')
        network = Networks.Ethereum
        client = Client(private_key='', network=network)
        print(f'''Python list (parsed from Etherscan):
{await client.contracts.get_abi(contract_address='0xE592427A0AEce92De3Edee1F18E0157C05861564')}
''')

        network.api.key = ''
        client = Client(private_key='', network=network)
        print(f'''JSON serialize string (parsed from contract code):
{await client.contracts.get_abi(contract_address='0xE592427A0AEce92De3Edee1F18E0157C05861564', raw_json=True)}''')

    @staticmethod
    async def get_contracts():
        """Get contract instances and print info about tokens."""
        print('\n--- get_contracts ---')
        tokens = (
            ('BNB', Networks.Ethereum, '0xB8c77482e45F1F44dE1745F52C74426C631bDD52'),
            ('ETH', Networks.BSC, '0x2170ed0880ac9a755fd29b2688956bd959f933f8'),
            ('OP', Networks.Optimism, '0x4200000000000000000000000000000000000042')
        )
        for symbol, network, address in tokens:
            client = Client(private_key='', network=network)
            contract = await client.contracts.get(contract_address=address)
            functions = await client.contracts.get_functions(contract=contract)
            print(f'''Name: {await contract.functions.name().call()}
Symbol: {await contract.functions.symbol().call()}
Total Supply: {Wei(await contract.functions.totalSupply().call()).Ether}
Functions ({len(functions)}):''')
            for function in functions:
                print(f'\t{function}')

            print('---')


class NFTs:
    @staticmethod
    async def get_info():
        """Get info about NFTs."""
        print('\n--- get_info ---')
        client = Client(private_key='', network=Networks.Ethereum)
        contract_addresses = (
            '0x12b180b635dd9f07a78736fb4e43438fcdb41555', '0x33c6eec1723b12c46732f7ab41398de45641fa42',
            '0x684e4ed51d350b4d76a3a07864df572d24e6dc4c', '0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d',
            '0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb', '0xa6c1c8ef0179071c16e066171d660da4ad314687',
            '0x34d85c9cdeb23fa97cb08333b511ac86e1c4e258', '0x23581767a106ae21c074b2276d25e5c3e136a68b',
            '0x49cf6f5d44e70224e2e23fdcdd2c053f30ada28b', '0x7d8e1909d22372e44c7b67bc7d5cba089eedca3d',
            '0x39ee2c7b3cb80254225884ca001f57118c8f21b6', '0x60e4d786628fea6478f785a6d7e704777c86a7c6')
        for contract_address in contract_addresses:
            nft_info = await client.nfts.get_info(contract_address, random.choice((random.randint(0, 9), None)))
            print(nft_info)
            for attribute in nft_info.attributes:
                print(f'\t{attribute}')

            print('---')


class Transactions:
    @staticmethod
    async def current_gas_price():
        """Get the current gas price."""
        print('\n--- current_gas_price ---')
        client = Client(private_key='', network=Networks.Ethereum)
        print(f'''{(await client.transactions.current_gas_price(w3=client.w3)).GWei} GWei''')

    @staticmethod
    async def estimate_gas():
        """Get the estimate gas limit for a transaction with specified parameters."""
        print('\n--- estimate_gas ---')
        client = Client(private_key=private_key)
        tx_params = {
            'nonce': 100,
            'gasPrice': (await client.transactions.current_gas_price(w3=client.w3)).Wei,
            'to': client.account.address,
            'value': 1000000
        }
        print(f'''{(await client.transactions.estimate_gas(w3=client.w3, tx_params=tx_params)).Wei} Wei''')

    @staticmethod
    async def auto_add_params():
        """Add 'chainId', 'from', 'gasPrice' and 'gas' parameters to transaction parameters if they are missing."""
        print('\n--- auto_add_params ---')
        client = Client(private_key=private_key)
        tx_params = {
            'nonce': 100,
            'to': client.account.address,
            'value': 1000000
        }
        print(f'''Source transaction params:
{tx_params}

Processed transaction params:
{await client.transactions.auto_add_params(tx_params=tx_params)}''')

    @staticmethod
    async def parse_params():
        """Parse params of the existing transaction."""
        print('\n--- parse_params ---')
        client = Client(private_key='', network=Networks.Ethereum)
        tx = Tx(tx_hash='0xd41a90a7c465a33e028cfc43e3b024c06d8f023ae4a42557269bad93e73edb6c')
        print(f'''Tx instance attribute:
{tx.params}

Tx instance function:
{await tx.parse_params(client=client)}

Tx instance attribute:
{tx.params}''')

    @staticmethod
    async def decode_input_data():
        """Decode input data using contract ABI."""
        print('\n--- decode_input_data ---')
        client = Client(private_key='', network=Networks.Ethereum)
        contract = await client.contracts.get(contract_address='0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f')
        tx_hash = '0xd41a90a7c465a33e028cfc43e3b024c06d8f023ae4a42557269bad93e73edb6c'
        tx = Tx(tx_hash=tx_hash)
        print(f'''Tx instance function:
{await tx.decode_input_data(client=client, contract=contract)}

Tx instance attributes:
{tx.function_identifier} {tx.input_data}

Transactions class function:
{await client.transactions.decode_input_data(client=client, contract=contract, tx_hash=tx_hash)}''')

    @staticmethod
    async def history():
        """Show the transaction history."""
        print('\n--- history ---')
        client = Client(private_key=private_key, network=Networks.Ethereum)
        address = '0x7E695e0f3BD9ba81EddAA800D06267d32E4CE484'
        history = await client.transactions.history(address=address, raw=True)
        print(f'''\t\t\tRaw
Coin: {len(history.coin)}
Internal: {len(history.internal)}
ERC-20: {len(history.erc20)}
ERC-721: {len(history.erc721)}

---
\t\t\tProcessed''')

        history = await client.transactions.history(address=address)
        print(f'''Coin: {len(history.coin.all)}
Internal: {len(history.internal.all)}
ERC-20: {len(history.erc20.all)}
ERC-721: {len(history.erc721.all)}
''')
        if history.coin:
            print('\nCoin:')
            for tx_hash, tx in history.coin.all.items():
                print(f'\t{tx}\n')

        if history.internal:
            print('\nInternal:')
            for tx_hash, tx in history.internal.all.items():
                print(f'\t{tx}\n')

        if history.erc20:
            print('\nERC20:')
            for tx_hash, tx in history.erc20.all.items():
                print(f'\t{tx}\n')

        if history.erc721:
            print('\nERC721:')
            for tx_hash, tx in history.erc721.all.items():
                print(f'\t{tx}\n')

    @staticmethod
    async def find_txs():
        """Find all transactions of interaction with the contract, in addition, you can filter transactions by the name of the contract function."""
        print('\n--- find_txs ---')
        client = Client(private_key='', network=Networks.Ethereum)
        txs = await client.transactions.find_txs(contract='0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f',
                                                 address='0x89D022F95dC5073B7479699044fDf6E3Bc74D3b3')
        print(f'All interaction transactions ({len(txs)}):')
        for tx_hash, tx in txs.items():
            print(f'\t{tx}\n')

        function_name = 'swapExactETHForTokens'
        txs = await client.transactions.find_txs(contract='0xd9e1ce17f2641f24ae83637ab66a2cca9c378b9f',
                                                 function_name=function_name,
                                                 address='0x89D022F95dC5073B7479699044fDf6E3Bc74D3b3')
        print(f'\n\n{function_name} transactions ({len(txs)}):')
        for tx_hash, tx in txs.items():
            print(f'\t{tx}\n')

    @staticmethod
    async def approved_amount():
        """Get approved amount of token."""
        print('\n--- approved_amount ---')
        client = Client(private_key='', network=Networks.Ethereum)
        token = await client.contracts.get(contract_address='0xf4d2888d29D722226FafA5d9B24F9164c092421E')
        spender = '0xe592427a0aece92de3edee1f18e0157c05861564'
        owner = '0x6a32729ae1a19f0cafd468d0082a1a9355167692'
        approved_amount = await client.transactions.approved_amount(token=token, spender=spender, owner=owner)
        print(f'''{owner} allowed {spender} to spend {approved_amount.Ether} {await token.functions.symbol().call()}''')

    @staticmethod
    async def send_coin():
        """Send transaction in the coin."""
        print('\n--- send_coin ---')
        client = Client(private_key=private_key)
        print(f'''Balance before sending: {(await client.wallet.balance()).Ether}
Raw tx:
{await client.transactions.send(token='', recipient=client.account.address, dry_run=True)}''')
        tx = await client.transactions.send(token='', recipient=client.account.address)
        receipt = await tx.wait_for_receipt(client=client)
        print(f'''Tx:
{tx}
Receipt:
{dict(receipt)}
Balance after sending: {(await client.wallet.balance()).Ether} {await get_coin_symbol(chain_id=client.network.chain_id)}''')

    @staticmethod
    async def send_token():
        """Send transaction in token."""
        print('\n--- send_token ---')
        client = Client(private_key=private_key)
        for contract, amount in ((await client.contracts.get('0x11fE4B6AE13d2a6055C8D9cF65c55bac32B5d844'), 10.5),
                                 ('0x11fE4B6AE13d2a6055C8D9cF65c55bac32B5d844', 9999999999)):
            if isinstance(contract, AsyncContract):
                contract_obj = contract
            else:
                contract_obj = await client.contracts.get(contract)

            print(
                f'{await contract_obj.functions.symbol().call()} balance before sending: {(await client.wallet.balance(contract_obj)).Ether}')
            tx = await client.transactions.send(token=contract, recipient=client.account.address, amount=amount)
            receipt = await tx.wait_for_receipt(client=client)
            print(f'''Tx:
{tx}
Receipt:
{dict(receipt)}
{await contract_obj.functions.symbol().call()} balance after sending: {(await client.wallet.balance(contract_obj)).Ether}
---
''')

    @staticmethod
    async def cancel_coin():
        """Cancel a transaction in coin."""
        print('\n--- cancel_coin ---')
        client = Client(private_key=private_key)
        tx = await client.transactions.send(token='', recipient=client.account.address, amount=0.05)
        print(f'Stuck tx:\n{tx}')
        success = await tx.cancel(client=client)
        print(f'Success: {success}')
        receipt = await tx.wait_for_receipt(client=client)
        print(f'''Tx:
{tx}
Receipt:
{dict(receipt)}
Balance after sending: {(await client.wallet.balance()).Ether} {await get_coin_symbol(chain_id=client.network.chain_id)}''')

    @staticmethod
    async def cancel_token():
        """Cancel a transaction in token."""
        print('\n--- cancel_token ---')
        client = Client(private_key=private_key)
        token = '0x11fE4B6AE13d2a6055C8D9cF65c55bac32B5d844'
        tx = await client.transactions.send(token=token, recipient=client.account.address)
        print(f'Stuck tx:\n{tx}')
        success = await tx.cancel(client=client)
        print(f'\nSuccess: {success}')
        receipt = await tx.wait_for_receipt(client=client)
        print(f'''Tx:
{tx}
Receipt:
{dict(receipt)}
Balance after sending: {(await client.wallet.balance(token=token)).Ether}''')

    @staticmethod
    async def speed_up_coin():
        """Speed up a transaction in coin."""
        print('\n--- speed_up_coin ---')
        client = Client(private_key=private_key)
        tx = await client.transactions.send(token='', recipient=client.account.address, amount=0.05)
        print(f'Stuck tx:\n{tx}')
        success = await tx.speed_up(client=client, gas_price=10)
        print(f'Success: {success}')
        receipt = await tx.wait_for_receipt(client=client)
        print(f'''Tx:
{tx}
Receipt:
{dict(receipt)}
Balance after sending: {(await client.wallet.balance()).Ether} {await get_coin_symbol(chain_id=client.network.chain_id)}''')

    @staticmethod
    async def speed_up_token():
        """Speed up a transaction in token."""
        print('\n--- speed_up_token ---')
        client = Client(private_key=private_key)
        token = '0x11fE4B6AE13d2a6055C8D9cF65c55bac32B5d844'
        tx = await client.transactions.send(token=token, recipient=client.account.address)
        print(f'Stuck tx:\n{tx}')
        success = await tx.speed_up(client=client, gas_price=10)
        print(f'\nSuccess: {success}')
        receipt = await tx.wait_for_receipt(client=client)
        print(f'''Tx:
{tx}
Receipt:
{dict(receipt)}
Balance after sending: {(await client.wallet.balance(token=token)).Ether}''')

    @staticmethod
    async def approve():
        """Approve token for swap."""
        print('\n--- approve ---')
        client = Client(private_key=private_key)
        tx = await client.transactions.approve(token='0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
                                               spender='0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45')
        receipt = await tx.wait_for_receipt(client=client)
        print(f'''Tx:
{tx}
Receipt:
{dict(receipt)}''')


class Miscellaneous:
    @staticmethod
    async def custom_network():
        """Initialize the custom network."""
        print('\n--- custom_network ---')
        network = Network(name='moonriver', rpc='https://rpc.api.moonriver.moonbeam.network')
        print(network)

    @staticmethod
    async def tx_args():
        """Use this to give human names to arguments and then get a tuple or list of arguments to send to transactions."""
        print('\n--- tx_args ---')
        client = Client(private_key=private_key)
        args = TxArgs(
            amount=1000000,
            address=client.account.address,
            pair=TxArgs(
                suource_token='0x7F5c764cBc14f9669B88837ca1490cCa17c31607',
                dest_token='0x94b008aA00579c1307B0EF2c499aD98a8ce58e58'
            ).list()
        )
        print(f'''{args}
{args.list()}
{args.tuple()}''')

    @staticmethod
    async def units():
        """Use these units when working with the library."""
        print('\n--- units ---')
        print(f'''Usage for coin:
{Ether(0.015200945)}

Usage for token:
{TokenAmount(amount=500.73467)}

Usage for gas price:
{GWei(14.64734)}''')

    @staticmethod
    async def unit_math_operations():
        """Example of mathematical operations on a Unit instance."""
        print('\n--- unit_math_operations ---')
        print(f'''Addition
100 + 20 + 5 = {(Wei(100) + 20 + Wei(5)).Wei}
4.1 + 1 + 2.0 = {(4.1 + GWei(1) + 2.0).GWei}
3020 + 100 + 8 = {(Wei(3020) + Wei(100) + 8).Wei}
0.5 + 0.1 + 0.03 = {(0.5 + 0.1 + Ether(0.03)).Ether}

Subtraction
100 - 20 - 5 = {(Wei(100) - 20 - 5).Wei}
4.1 - 1 - 2.0 = {(4.1 - GWei(1) - 2.0).GWei}
3020 - 100 - 8 = {(Wei(3020) - Wei(100) - 8).Wei}
0.5 - 0.1 - 0.03 = {(0.5 - 0.1 - Ether(0.03)).Ether}

Multiplication
100 * 20 * 5 = {(Wei(100) * 20 * 5).Wei}
4.1 * 1 * 2.0 = {(4.1 * GWei(1) * 2.0).GWei}
3020 * 100 * 8 = {(Wei(3020) * Wei(100) * 8).Wei}
0.5 * 0.1 * 0.03 = {(0.5 * 0.1 * Ether(0.03)).Ether}

Division
100 / 20 / 5 = {(Wei(100) / 20 / 5).Wei}
4.1 / 1 / 2.0 = {(4.1 / GWei(1) / 2.0).GWei}
3020 / 100 / 8 = {(Wei(3020) / Wei(100) / 8).Wei}
0.5 / 0.1 / 0.03 = {(0.5 / 0.1 / Ether(0.03)).Ether}

Less than
100 < 20: {Wei(100) < 20}
1 < 2.0 < 4.1: {GWei(1) < 2.0 < 4.1}
100 < 8 < 3020: {Wei(100) < 8 < Wei(3020)}
0.03 < 0.5: {0.03 < Ether(0.5)}

Less than or equal to
100 <= 100: {Wei(100) <= 100}
4.1 <= 1: {4.1 <= GWei(1)}
100 <= 3020: {Wei(100) <= Wei(3020)}
0.5 <= 0.03: {0.5 <= Ether(0.03)}

Equal
100 == 20: {Wei(100) == 20}
4.1 == 1: {4.1 == GWei(1)}
3020 == 3020: {3020 == Wei(3020)}
0.5 == 0.5: {0.5 == Ether(0.5)}

Not equal to
100 != 20: {Wei(100) != 20}
4.1 != 4.1: {4.1 != GWei(4.1)}
3020 != 3020: {3020 != Wei(3020)}
0.03 != 0.5: {Ether(0.03) != 0.5}

Great than
100 > 20: {Wei(100) > 20}
4.1 > 4.1: {4.1 > GWei(4.1)}
8 > 3020: {8 > Wei(3020)}
0.5 > 0.03: {0.5 > Ether(0.03)}

Great and equal
100 >= 100: {Wei(100) >= 100}
2.0 >= 4.1: {2.0 >= GWei(4.1)}
8 >= 3020: {8 >= Wei(3020)}
0.5 >= 0.03: {0.5 >= Ether(0.03)}''')

    @staticmethod
    async def unit_advanced_math_operations():
        """Example of advanced mathematical operations on a Unit instance."""
        print('\n--- unit_advanced_math_operations ---')
        amount = Wei(100)
        print(f'Before the transformation: {amount.Wei}')
        amount += 20 + Wei(5)
        print(f'After: {amount.Wei}\n')

        amount = GWei(4.1)
        print(f'Before the transformation: {amount.GWei}')
        amount -= 2.0
        # amount -= 2.0 - GWei(1)  # Works incorrect
        print(f'After: {amount.GWei}\n')

        amount = Wei(3020)
        print(f'Before the transformation: {amount.Wei}')
        amount *= Wei(100) * 8
        print(f'After: {amount.Wei}\n')

        amount = Ether(0.5)
        print(f'Before the transformation: {amount.Ether}')
        amount /= 0.1
        # amount /= 0.1 - Ether(0.03)  # Works incorrect
        print(f'After: {amount.Ether}')

    @staticmethod
    async def token_amount_math_operations():
        """Example of mathematical operations on a TokenAmount instance."""
        print('\n--- token_amount_math_operations ---')
        print(f'''Addition
100 + 20.0 + 5 = {(TokenAmount(100, decimals=6) + 20.0 + TokenAmount(5, decimals=6)).Ether}

Subtraction
100 - 20.0 - 5 = {(TokenAmount(100, decimals=6) - 20.0 - TokenAmount(5, decimals=6)).Ether}

Multiplication
100 * 20.0 * 5 = {(TokenAmount(100, decimals=6) * 20.0 * TokenAmount(5, decimals=6)).Ether}

Division
100 / 20.0 / 5 = {(TokenAmount(100, decimals=6) / 20.0 / TokenAmount(5, decimals=6)).Ether}

Less than
100 < 20.0: {TokenAmount(100, decimals=6) < 20.0}
1 < 2.0 < 4.1: {TokenAmount(1, decimals=6) < 2.0 < TokenAmount(4.1, decimals=6) < 20.0}

Less than or equal to
100 <= 100.0: {TokenAmount(100, decimals=6) <= 100.0}
4.1 <= 1: {4.1 <= TokenAmount(1, decimals=6)}

Equal
20.0 == 100: {20.0 == TokenAmount(100, decimals=6)}
4.1 == 4.1: {TokenAmount(4.1, decimals=6) == 4.1}

Not equal to
100 != 20: {TokenAmount(100, decimals=6) != 20.0}
4.1 != 4.1: {4.1 != TokenAmount(4.1, decimals=6)}

Great than
100 > 20: {100.0 > TokenAmount(20, decimals=6)}
4.1 > 4.1: {TokenAmount(4.1, decimals=6) > 4.1}

Great and equal
100 >= 100: {TokenAmount(100, decimals=6) >= 100.0}
2.0 >= 4.1: {2.0 >= TokenAmount(4.1, decimals=6)}''')

    @staticmethod
    async def token_amount_advanced_math_operations():
        """Example of advanced mathematical operations on a TokenAmount instance."""
        print('\n--- token_amount_advanced_math_operations ---')
        amount = TokenAmount(100, decimals=6)
        print(f'Before the transformation: {amount.Ether}')
        amount += 20.0 + TokenAmount(5, decimals=6)
        print(f'After: {amount.Ether}\n')

        amount = TokenAmount(100, decimals=6)
        print(f'Before the transformation: {amount.Ether}')
        amount -= 20.0
        # amount -= 20.0 - TokenAmount(5, decimals=6)  # Works incorrect
        print(f'After: {amount.Ether}\n')

        amount = TokenAmount(100, decimals=6)
        print(f'Before the transformation: {amount.Ether}')
        amount *= 20.0 * TokenAmount(5, decimals=6)
        print(f'After: {amount.Ether}\n')

        amount = TokenAmount(100, decimals=6)
        print(f'Before the transformation: {amount.Ether}')
        amount /= 20.0
        # amount /= 20.0 / TokenAmount(5, decimals=6)  # Works incorrect
        print(f'After: {amount.Ether}')

    @staticmethod
    async def change_decimals():
        """Leave the Ether amount and change the Wei based on the new decimals."""
        print('\n--- change_decimals ---')
        token = TokenAmount(amount=500.73467)
        print(f'''Instance from Ether amount: {token}
Change decimals and get Wei: {token.change_decimals(new_decimals=6)}
Instance with changed decimals: {token}
Instance from Wei amount: {TokenAmount(amount=500734670000000008192, wei=True)}''')


async def main() -> None:
    print('\n--------- Account ---------')
    account = Account()
    await account.generate_wallets()
    await account.show_coin_balance()
    await account.show_token_balance()

    print('\n--------- Contracts ---------')
    contracts = Contracts()
    await contracts.get_abi()
    await contracts.get_contracts()

    print('\n--------- NFTs ---------')
    nfts = NFTs()
    await nfts.get_info()

    print('\n--------- Transactions ---------')
    transactions = Transactions()
    await transactions.current_gas_price()
    await transactions.estimate_gas()
    await transactions.auto_add_params()
    await transactions.parse_params()
    await transactions.decode_input_data()
    await transactions.find_txs()
    await transactions.approved_amount()
    await transactions.history()
    await transactions.send_coin()
    await transactions.send_token()
    await transactions.cancel_coin()
    await transactions.cancel_token()
    await transactions.speed_up_coin()
    await transactions.speed_up_token()
    await transactions.approve()

    print('\n--------- Miscellaneous ---------')
    miscellaneous = Miscellaneous()
    await miscellaneous.custom_network()
    await miscellaneous.tx_args()
    await miscellaneous.units()
    await miscellaneous.unit_math_operations()
    await miscellaneous.unit_advanced_math_operations()
    await miscellaneous.token_amount_math_operations()
    await miscellaneous.token_amount_advanced_math_operations()
    await miscellaneous.change_decimals()


if __name__ == '__main__':
    private_key = str(os.getenv('PRIVATE_KEY'))
    if private_key:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

    else:
        print("Specify the private key in the 'PRIVATE_KEY' variable in the .env file!")
