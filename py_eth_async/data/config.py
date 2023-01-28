import os

from dotenv import load_dotenv

load_dotenv()

ETHEREUM_APIKEY = str(os.getenv('ETHEREUM_APIKEY'))
ARBITRUM_APIKEY = str(os.getenv('ARBITRUM_APIKEY'))
OPTIMISM_APIKEY = str(os.getenv('OPTIMISM_APIKEY'))
BSC_APIKEY = str(os.getenv('BSC_APIKEY'))
POLYGON_APIKEY = str(os.getenv('POLYGON_APIKEY'))
AVALANCHE_APIKEY = str(os.getenv('AVALANCHE_APIKEY'))
MOONBEAM_APIKEY = str(os.getenv('MOONBEAM_APIKEY'))
FANTOM_APIKEY = str(os.getenv('FANTOM_APIKEY'))
GNOSIS_APIKEY = str(os.getenv('GNOSIS_APIKEY'))
HECO_APIKEY = str(os.getenv('HECO_APIKEY'))
GOERLI_APIKEY = str(os.getenv('GOERLI_APIKEY'))
SEPOLIA_APIKEY = str(os.getenv('SEPOLIA_APIKEY'))
