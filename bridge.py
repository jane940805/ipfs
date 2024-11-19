from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware #Necessary for POA chains
import json
import sys
from pathlib import Path

source_chain = 'avax'
destination_chain = 'bsc'
contract_info = "contract_info.json"

def connectTo(chain):
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'bsc':
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['avax','bsc']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

def getContractInfo(chain):
    """
        Load the contract_info file into a dictinary
        This function is used by the autograder and will likely be useful to you
    """
    p = Path(__file__).with_name(contract_info)
    try:
        with p.open('r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( "Failed to read contract info" )
        print( "Please contact your instructor" )
        print( e )
        sys.exit(1)

    return contracts[chain]



# def scanBlocks(chain):
#     """
#         chain - (string) should be either "source" or "destination"
#         Scan the last 5 blocks of the source and destination chains
#         Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
#         When Deposit events are found on the source chain, call the 'wrap' function the destination chain
#         When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
#     """

#     if chain not in ['source','destination']:
#         print( f"Invalid chain: {chain}" )
#         return
    
#         #YOUR CODE HERE


def scanBlocks(chain):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function on the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    # Get the web3 instance for the given chain
    w3 = connectTo(source_chain if chain == "source" else destination_chain)
    contract_info = getContractInfo(source_chain if chain == "source" else destination_chain)

    # Get the contract details
    contract_address = contract_info['address']
    contract_abi = contract_info['abi']

    # Connect to the contract
    contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=contract_abi)

    # Get the latest block
    latest_block = w3.eth.block_number

    # Scan the last 5 blocks
    start_block = max(0, latest_block - 5)
    for block_number in range(start_block, latest_block + 1):
        block = w3.eth.get_block(block_number, full_transactions=True)

        for tx in block['transactions']:
            # Check if the transaction involves the contract
            if tx['to'] and Web3.to_checksum_address(tx['to']) == contract.address:
                try:
                    # Decode the logs to identify the event
                    receipt = w3.eth.get_transaction_receipt(tx['hash'])
                    events = contract.events.Deposit().process_receipt(receipt) if chain == "source" else contract.events.Unwrap().process_receipt(receipt)

                    for event in events:
                        # Extract event data
                        event_data = event['args']
                        print(f"Detected event on {chain}: {event_data}")

                        if chain == "source":
                            # Call wrap function on the destination chain
                            dest_w3 = connectTo(destination_chain)
                            dest_contract_info = getContractInfo(destination_chain)
                            dest_contract = dest_w3.eth.contract(
                                address=Web3.to_checksum_address(dest_contract_info['address']),
                                abi=dest_contract_info['abi']
                            )
                            wrap_tx = dest_contract.functions.wrap(
                                event_data['amount'], event_data['to']
                            ).build_transaction({
                                'from': dest_w3.eth.default_account,
                                'nonce': dest_w3.eth.get_transaction_count(dest_w3.eth.default_account),
                                'gas': 2000000,
                                'gasPrice': dest_w3.toWei('10', 'gwei'),
                            })
                            signed_tx = dest_w3.eth.account.sign_transaction(wrap_tx, private_key='YOUR_PRIVATE_KEY')
                            dest_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                            print("Wrap function called on destination chain.")

                        elif chain == "destination":
                            # Call withdraw function on the source chain
                            src_w3 = connectTo(source_chain)
                            src_contract_info = getContractInfo(source_chain)
                            src_contract = src_w3.eth.contract(
                                address=Web3.to_checksum_address(src_contract_info['address']),
                                abi=src_contract_info['abi']
                            )
                            withdraw_tx = src_contract.functions.withdraw(
                                event_data['amount'], event_data['from']
                            ).build_transaction({
                                'from': src_w3.eth.default_account,
                                'nonce': src_w3.eth.get_transaction_count(src_w3.eth.default_account),
                                'gas': 2000000,
                                'gasPrice': src_w3.toWei('10', 'gwei'),
                            })
                            signed_tx = src_w3.eth.account.sign_transaction(withdraw_tx, private_key='YOUR_PRIVATE_KEY')
                            src_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                            print("Withdraw function called on source chain.")

                except Exception as e:
                    print(f"Error processing transaction {tx['hash'].hex()}: {e}")
