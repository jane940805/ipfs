
from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware #Necessary for POA chains
import json
import sys
from pathlib import Path
import time

source_chain = 'avax'
destination_chain = 'bsc'
source = 'avax'
destination = 'bsc'
contract_info = "contract_info.json"

def connectTo(chain):
    #student add
    if chain not in ['avax','bsc']:
        print(f"{chain} is not a valid option for 'connect_to()'")
    ## end
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



def scanBlocks(chain):
    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return
    
        #YOUR CODE HERE
    if chain == 'source':
        chain_name = 'avax'
        address = "0x1aE13D2d15870440f2623649e2Dc9c1833536aD0"
    else:
        chain_name = 'bsc'
        address = "0x469fDBE953Ed443252c19161A6Ed8c8bd7957850"
        
    w3 = connectTo(chain_name)
    contract_info = getContractInfo(chain)
    contract_abi = contract_info["abi"]
    contract = w3.eth.contract(address=w3.to_checksum_address(address), abi=contract_abi)
    admin_private_key = 'e1bef06dbde74fae23a2e93b6e7c707abe89925b8dd8541fd4d5a587a109508a'
    admin_address = '0x28550C5a58b6fA26b58a20B1377431E507322b79'

    latest_block = w3.eth.block_number
    start_block = latest_block - 4
    for block_num in range(start_block, latest_block + 1):
        if chain == 'source':
            event_filter = contract.events.Deposit.create_filter(fromBlock=block_num,toBlock=block_num)
            deposit_events = event_filter.get_all_entries()
            for event in deposit_events:
                token = event.args.token
                recipient = event.args.recipient
                amount = event.args.amount
                print(f"Deposit event detected. Token: {token}, Recipient: {recipient}, Amount: {amount}")
                destination_w3 = connectTo('bsc')
                destination_contract_info = getContractInfo('destination')
                destination_contract_abi = destination_contract_info["abi"]
                destination_address = "0x469fDBE953Ed443252c19161A6Ed8c8bd7957850"
                destination_contract = destination_w3.eth.contract(address=destination_w3.to_checksum_address(destination_address), abi=destination_contract_abi)
                transaction = destination_contract.functions.wrap(token, recipient, amount).build_transaction({
                    'from': admin_address,
                    'gas': 500000,
                    'gasPrice': destination_w3.eth.gas_price,
                    'nonce': destination_w3.eth.get_transaction_count(admin_address),
                })
                signed_transaction = destination_w3.eth.account.sign_transaction(transaction, admin_private_key)
                tx_hash = destination_w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
                print(f"wrap() transaction sent")

        if chain == 'destination':
            event_filter = contract.events.Unwrap.create_filter(fromBlock=block_num,toBlock=block_num)
            unwrap_events = event_filter.get_all_entries()
            for event in unwrap_events:
                underlying_token = event.args.underlying_token
                token = event.args.wrapped_token
                frm = event.args.frm
                to = event.args.to
                amount = event.args.amount
                print(f"Unwrap event detected. underlying_token: {underlying_token}, Token:{token}, From: {frm}, To:{to}, Amount: {amount}")
                source_w3 = connectTo('avax')
                source_contract_info = getContractInfo('source')
                source_contract_abi = source_contract_info["abi"]
                source_address = "0x1aE13D2d15870440f2623649e2Dc9c1833536aD0"
                source_contract = source_w3.eth.contract(address=source_w3.to_checksum_address(source_address), abi=source_contract_abi)
                transaction = source_contract.functions.withdraw(underlying_token, to, amount).build_transaction({
                    'from': admin_address,
                    'gas': 3000000,
                    'gasPrice': source_w3.eth.gas_price,
                    'nonce': source_w3.eth.get_transaction_count(admin_address),
                })
                signed_tx = source_w3.eth.account.sign_transaction(transaction, admin_private_key)
                tx_hash = source_w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print(f"withdraw() transaction sent")
        
        time.sleep(5)
