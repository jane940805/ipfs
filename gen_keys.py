from web3 import Web3
import eth_account
import os
from eth_account import Account


def get_keys(challenge,keyId = 0, filename = "eth_mnemonic.txt"):
    """
    Generate a stable private key
    challenge - byte string
    keyId (integer) - which key to use
    filename - filename to read and store mnemonics

    Each mnemonic is stored on a separate line
    If fewer than (keyId+1) mnemonics have been generated, generate a new one and return that
    """
    # Replace this with your private key (keep this secure and do not share it)
    private_key = "e1bef06dbde74fae23a2e93b6e7c707abe89925b8dd8541fd4d5a587a109508a"

	#YOUR CODE HERE

    # Check if the mnemonic file exists; if not, create it
    if not os.path.exists(filename):
        open(filename, 'w').close()

    # Read existing mnemonics
    with open(filename, 'r') as f:
        mnemonics = [line.strip() for line in f.readlines()]

    # Create a Web3 instance and an account using the private key
    w3 = Web3()
    eth_addr = '0x28550C5a58b6fA26b58a20B1377431E507322b79'

    # Encode the challenge message
    msg = eth_account.messages.encode_defunct(challenge)

    # Sign the message using the account
    sig = w3.eth.account.sign_message(msg, private_key=private_key)

    assert eth_account.Account.recover_message(msg, signature=sig.signature.hex()) == eth_addr, "Failed to sign message properly"

    # Return the signature and Ethereum address
    return sig, eth_addr

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr= get_keys(challenge=challenge,keyId=i)
        print( addr )

