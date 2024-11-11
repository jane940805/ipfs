from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware  # Necessary for POA chains
import json
from datetime import datetime
import pandas as pd

eventfile = 'deposit_logs.csv'

def scanBlocks(chain, start_block, end_block, contract_address):
    """
    chain - string (Either 'bsc' or 'avax')
    start_block - integer first block to scan
    end_block - integer last block to scan
    contract_address - the address of the deployed contract

    This function reads "Deposit" events from the specified contract, 
    and writes information about the events to the file "deposit_logs.csv"
    """
    # Select the appropriate RPC URL based on the chain
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == 'bsc':
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    else:
        raise ValueError("Unsupported chain. Use either 'avax' or 'bsc'.")

    # Initialize web3 instance and add the POA middleware for compatibility
    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Define the ABI for the Deposit event
    DEPOSIT_ABI = json.loads('[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "token", "type": "address" }, { "indexed": true, "internalType": "address", "name": "recipient", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "Deposit", "type": "event" }]')
    contract = w3.eth.contract(address=contract_address, abi=DEPOSIT_ABI)

    # Determine the starting and ending blocks if set to 'latest'
    if start_block == "latest":
        start_block = w3.eth.get_block_number()
    if end_block == "latest":
        end_block = w3.eth.get_block_number()

    # Check for a valid block range
    if end_block < start_block:
        raise ValueError("end_block cannot be less than start_block")

    # Function to process and save events to CSV
    def log_events(events):
        rows = []
        for event in events:
            row = {
                "chain": chain,
                "token": event["args"]["token"],
                "recipient": event["args"]["recipient"],
                "amount": event["args"]["amount"],
                "transactionHash": event["transactionHash"].hex(),
                "address": contract_address
            }
            rows.append(row)
        # Append to CSV
        df = pd.DataFrame(rows)
        df.to_csv(eventfile, mode='a', index=False, header=not pd.io.common.file_exists(eventfile))

    # Scan blocks for Deposit events
    if end_block - start_block < 30:  # Direct filter if range is small
        event_filter = contract.events.Deposit.create_filter(
            fromBlock=start_block, toBlock=end_block
        )
        events = event_filter.get_all_entries()
        log_events(events)
    else:  # Loop through each block if the range is large
        for block_num in range(start_block, end_block + 1):
            event_filter = contract.events.Deposit.create_filter(
                fromBlock=block_num, toBlock=block_num
            )
            events = event_filter.get_all_entries()
            log_events(events)

    print("Scanning completed and events logged to deposit_logs.csv.")
