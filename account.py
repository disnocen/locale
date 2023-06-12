from utils import *
import web3 as w3
# import hashlib
# import eth_keys.datatypes as ekt
from eth_account import Account
# import eth_keys
from eth_keys.constants import SECPK1_N, SECPK1_P
# from eth_hash.auto import keccak
# from eth_keys.backends.native.ecdsa import decode_public_key, encode_raw_public_key, private_key_to_public_key
# from eth_keys.backends.native.jacobian import fast_multiply, fast_add
# from  eth_utils.encoding import big_endian_to_int
from utils import *
# from eth_keys import private_key_to_public_key
import os


def _sum_of_priv_keys(key1, key2):
    # assume that both keys are hex
    new_key = int(key1, 16) + int(key2, 16) % SECPK1_N
    return new_key


def get_sum_account(key1, key2):
    new_secret_key = _sum_of_priv_keys(key1, key2)
    new_account = Account.from_key(new_secret_key)
    return new_account


# Connect to the local node
w3 = w3.Web3(w3.HTTPProvider('http://127.0.0.1:8545'))

# Print the current block number
print("the current block number is: ", w3.eth.block_number)

# Print the current gas price
print("the current gas price is: ", w3.eth.gas_price)

# import account from private key string

operator_secret_key = "0x6948f00fdfb6f8439fe9f66b200f9ed7c85c1a755497114c35a0d1166f709310"
current_hash = "aabb"


operator_account = Account.from_key(operator_secret_key)
operator_address_from_ganace = "0x9B10BCC7cd3336aD330f46dce780B751F900e83f"
assert operator_address_from_ganace == operator_account.address
print("Operator address:", operator_account.address)

new_account = get_sum_account(operator_secret_key, current_hash)
print("New address:", new_account.address)

tx_hash = w3.eth.send_transaction({
    'from': operator_account.address,
    'to': new_account.address,
    'value': w3.to_wei(3, 'ether'),
})

# Wait for the transaction to be mined, and get the transaction receipt
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Print the transaction receipt
print("the transaction receipt is: ", tx_receipt)

# Print the transaction receipt gas used
print("the transaction receipt gas used is: ", tx_receipt.gasUsed)
