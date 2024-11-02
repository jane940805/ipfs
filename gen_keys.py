from web3 import Web3
import eth_account
import os
from eth_account import Account


# Replace this line with your actual private key (ensure you store it securely and do not share it in public code)
PRIVATE_KEY = "your_private_key_here"  # Replace with your actual private key




def get_keys(challenge,keyId = 0, filename = "eth_mnemonic.txt"):
    """
    Generate a stable private key
    challenge - byte string
    keyId (integer) - which key to use
    filename - filename to read and store mnemonics

    Each mnemonic is stored on a separate line
    If fewer than (keyId+1) mnemonics have been generated, generate a new one and return that
    """

    w3 = Web3()

	#YOUR CODE HERE

    # # Check if the mnemonic file exists; if not, create it
    # if not os.path.exists(filename):
    #     open(filename, 'w').close()

    # # Read existing mnemonics
    # with open(filename, 'r') as f:
    #     mnemonics = [line.strip() for line in f.readlines()]

    # Create an account instance from the provided private key
    account = eth_account.Account.from_key(PRIVATE_KEY)
    eth_addr = account.address

    # Sign the challenge message
    msg = eth_account.messages.encode_defunct(challenge)
    sig = w3.eth.account.sign_message(msg, private_key=PRIVATE_KEY)

    # Ensure the signature can be recovered back to the correct address
    assert eth_account.Account.recover_message(msg, signature=sig.signature.hex()) == eth_addr, \
        f"Failed to sign message properly"

    # Return the signature and account address
    return sig, eth_addr

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr= get_keys(challenge=challenge,keyId=i)
        print( addr )

