import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers.rpc import HTTPProvider

'''If you use one of the suggested infrastructure providers, the url will be of the form
now_url  = f"https://eth.nownodes.io/{now_token}"
alchemy_url = f"https://eth-mainnet.alchemyapi.io/v2/{alchemy_token}"
infura_url = f"https://mainnet.infura.io/v3/{infura_token}"
'''


def connect_to_eth():
	url = "https://eth-mainnet.g.alchemy.com/v2/iZu9NnlgGt50L9PhmENlgvQYgyLUZjJS"  # FILL THIS IN
	w3 = Web3(HTTPProvider(url))
	assert w3.is_connected(), f"Failed to connect to provider at {url}"
	return w3


def connect_with_middleware(contract_json):
	with open(contract_json, "r") as f:
		d = json.load(f)
		d = d['bsc']
		address = d['address']
		abi = d['abi']

	
	# Connect to BNB testnet using an HTTP provider
	# Replace the provider URL with the actual BNB testnet provider URL (you may use a public node or Infura-like services)
	bnb_testnet_provider = "https://eth-mainnet.g.alchemy.com/v2/iZu9NnlgGt50L9PhmENlgvQYgyLUZjJS"
		
	# Initialize the Web3 object
	w3 = Web3(Web3.HTTPProvider(bnb_testnet_provider))

	# Check if the connection is successful
	if not w3.isConnected():
		raise Exception("Unable to connect to the BNB testnet")

	w3.middleware_onion.inject(geth_poa_middleware, layer=0)

	assert w3.is_connected(), "Failed to connect to Binance Smart Chain"

	# Instantiate the contract
	contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

	# Return the Web3 object and the contract instance
	return w3, contract



if __name__ == "__main__":
	connect_to_eth()
