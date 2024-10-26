from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
import requests
import json
import time

bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.toChecksumAddress(bayc_address)

#You will need the ABI to connect to the contract
#The file 'abi.json' has the ABI for the bored ape contract
#In general, you can get contract ABIs from etherscan
#https://api.etherscan.io/api?module=contract&action=getabi&address=0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D
with open('/home/codio/workspace/abi.json', 'r') as f:
	abi = json.load(f) 

############################
#Connect to an Ethereum node
api_url = "https://mainnet.infura.io/v3/2c3d72dd622d4fc1a9d2999566ddbc32"
provider = HTTPProvider(api_url)
web3 = Web3(provider)
contract = web3.eth.contract(address=contract_address, abi=abi)

def get_ape_info(apeID):
	assert isinstance(apeID,int), f"{apeID} is not an int"
	assert 1 <= apeID, f"{apeID} must be at least 1"

	data = {'owner': "", 'image': "", 'eyes': "" }
	
	#YOUR CODE HERE	
    # Connect to Ethereum

    # Define contract address and ABI (replace these with actual contract details)
	contract = web3.eth.contract(address=contract_address, abi=abi)
	
    # Get owner and token URI from the contract
	data['owner'] = contract.functions.ownerOf(apeID).call()
	token_uri = contract.functions.tokenURI(apeID).call()
	
	# Fetch metadata from IPFS and parse for image and eyes
	uri_address = "https://gateway.pinata.cloud/ipsf" + token_uri[7:]
	metadata = requests.get(uri_address).json()

	data['image'] = metadata.get("image")
	data['eyes'] = next(
        (trait["value"] for trait in metadata["attributes"] if trait["trait_type"] == "Eyes"), 
        None
    )

    # Verify output format
	assert isinstance(data,dict), f'get_ape_info{apeID} should return a dict' 
	assert all( [a in data.keys() for a in ['owner','image','eyes']] ), f"return value should include the keys 'owner','image' and 'eyes'"
	return data

