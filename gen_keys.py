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

    w3 = Web3()

	#YOUR CODE HERE

    # Check if the mnemonic file exists; if not, create it
    if not os.path.exists(filename):
        open(filename, 'w').close()

    # Read existing mnemonics
    with open(filename, 'r') as f:
        mnemonics = [line.strip() for line in f.readlines()]

    # Ensure there is a mnemonic for the requested keyId
    if keyId >= len(mnemonics):
        # Generate a new mnemonic and append it to the file
        new_mnemonic = Account.create().key.hex()
        mnemonics.append(new_mnemonic)
        with open(filename, 'a') as f:
            f.write(new_mnemonic + '\n')

    # Use the mnemonic at the specified keyId to create an account
    private_key = 0x204dbfbf1496b9a13f16caa06588df39947c232d89ade1f8ebadbc8dde129ca6
    acct = 0x94Bf794BBd6909441545511F9A4Fd2C585dF723e

    # Encode and sign the challenge message
    msg = eth_account.messages.encode_defunct(challenge)
    sig = w3.eth.account.sign_message(msg, private_key=acct.key)

    # Verify the address from the signature
    eth_addr = acct.address
    assert eth_account.Account.recover_message(msg, signature=sig.signature) == eth_addr, "Failed to sign message properly"

    #return sig, acct #acct contains the private key
    return sig, eth_addr

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr= get_keys(challenge=challenge,keyId=i)
        print( addr )

