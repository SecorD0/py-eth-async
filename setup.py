import os

from setuptools import setup, find_packages

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as fh:
    long_description = '\n' + fh.read()

setup(
    name='py-eth-async',
    version='1.10.4',
    license='Apache-2.0',
    author='SecorD',
    description='',
    long_description_content_type='text/markdown',
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'aiohttp-socks==0.8.0', 'aiohttp==3.9.3', 'eth-account==0.8.0',
        'evmdasm @ git+https://github.com/SecorD0/evmdasm@e8389f223746a0d8c94c627397d0dc639633e869',
        'fake-useragent', 'pretty-utils @ git+https://github.com/SecorD0/pretty-utils@main', 'PySocks==1.7.1',
        'python-dotenv==0.21.1', 'web3 @ git+https://github.com/ethereum/web3.py@v6.0.0-beta.9'
    ],
    keywords=[
        'eth', 'pyeth', 'py-eth', 'ethpy', 'eth-py', 'web3', 'pyweb3', 'py-web3', 'web3py', 'web3-py', 'async-eth',
        'pyethasync', 'py-eth-async', 'asyncethpy', 'async-eth-py', 'async-web3', 'pyweb3-async', 'py-web3-async',
        'async-web3py', 'async-web3-py'
    ],
    classifiers=[
        'Programming Language :: Python :: 3.8'
    ]
)
