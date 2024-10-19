import requests
import json


# Pinata API endpoint
PINATA_BASE_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
PINATA_API_KEY = "3674e742b1c881f1f6e2"
PINATA_SECRET_API_KEY = "0c7e8bcde90223b9875836425bc1be341cb05559c308fb98018c4d1ca57855df"



def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	#YOUR CODE HERE
    # Convert the dictionary to JSON format
	json_data = json.dumps(data)
    
    # Prepare headers for Pinata API
	headers = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY,
        "Content-Type": "application/json"
    }
    
    # Make the request to Pinata
	response = requests.post(PINATA_BASE_URL, headers=headers, json=data)
    
	if response.status_code == 200:
		cid = response.json()["IpfsHash"]
		return cid
	else:
		raise Exception(f"Failed to pin data to IPFS: {response.status_code} {response.text}")


def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE	
    # Use Pinata gateway to access the content
	gateway_url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    
    # Fetch the data from IPFS
	response = requests.get(gateway_url)
    
	if response.status_code == 200:
		data = response.json()  # Assume the content is JSON
		assert isinstance(data, dict), "get_from_ipfs should return a dict"
		return data
	else:
		raise Exception(f"Failed to retrieve data from IPFS: {response.status_code} {response.text}")