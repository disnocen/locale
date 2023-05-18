import web3 as w3
import hashlib 
import eth_keys.datatypes as ekt
from eth_account import Account
import eth_keys
from eth_keys.constants import SECPK1_N, SECPK1_P
from eth_hash.auto import keccak 
from eth_keys.backends.native.ecdsa import decode_public_key, encode_raw_public_key, private_key_to_public_key
from eth_keys.backends.native.jacobian import fast_multiply, fast_add 
from  eth_utils.encoding import big_endian_to_int
from utils import *
# from eth_keys import private_key_to_public_key
import os


def priv_key_to_number(priv_key):
    if not isinstance(priv_key, ekt.PrivateKey):
        raise TypeError("priv_key must be a PrivateKey")
    
    # check if related public key is even or odd
    # if priv_key.public_key.to_compressed_bytes()[1] == 2:
    #     # if even, add 2^256 to the private key
    #     priv_key_as_number = SECPK1_N  - big_endian_to_int(priv_key._raw_key) 
    # else:
    #     priv_key_as_number = big_endian_to_int(priv_key._raw_key)

    # get the hex string of the private key
    priv_key_as_number = big_endian_to_int(priv_key._raw_key) % SECPK1_N
    # return the private key
    return priv_key_as_number


def sum_private_keys(priv_key1, priv_key2):
    priv_key1_as_number = priv_key_to_number(priv_key1)
    priv_key2_as_number = priv_key_to_number(priv_key2)


    # priv_key1_as_number = priv_key1_as_number if has_even_y(priv_key1) else SECPK1_N - priv_key1_as_number
    # priv_key2_as_number = priv_key2_as_number if has_even_y(priv_key2) else SECPK1_N - priv_key2_as_number
    # sum the private keys
    sum_priv_key_as_number = (priv_key1_as_number + priv_key2_as_number) % SECPK1_N

    # number to hex
    sum_priv_key_as_hex = hex(sum_priv_key_as_number)[2:]
    print("sum_priv_key_as_hex" , sum_priv_key_as_hex)
    print("sum_priv_key_as_hex length" , len(sum_priv_key_as_hex))

    if len(sum_priv_key_as_hex) < 64:
        sum_priv_key_as_hex = "0" * (64 - len(sum_priv_key_as_hex)) + sum_priv_key_as_hex

    # hex to private key
    sum_priv_key = ekt.PrivateKey(bytes.fromhex(sum_priv_key_as_hex))

    if not has_even_y(sum_priv_key):
        sum_priv_key_as_number = SECPK1_N - sum_priv_key_as_number
        sum_priv_key_as_hex = hex(sum_priv_key_as_number)[2:]
        sum_priv_key = ekt.PrivateKey(bytes.fromhex(sum_priv_key_as_hex))

    # return the sum
    return sum_priv_key

def x(P):
    return P[0]

def y(P):
    return P[1]

def sum_public_keys2(P1, P2): 
    p = SECPK1_P
    P1 = decode_public_key(P1.to_bytes())
    P2 = decode_public_key(P2.to_bytes())
    if P1 is None:
        return P2
    if P2 is None:
        return P1
    if (x(P1) == x(P2)) and (y(P1) != y(P2)):
        return None
    if P1 == P2:
        lam = (3 * x(P1) * x(P1) * pow(2 * y(P1), p - 2, p)) % p
    else:
        lam = ((y(P2) - y(P1)) * pow(x(P2) - x(P1), p - 2, p)) % p
    x3 = (lam * lam - x(P1) - x(P2)) % p
    public_key_raw =  (x3, (lam * (x(P1) - x3) - y(P1)) % p)

    public_key_sum = ekt.PublicKey(encode_raw_public_key(public_key_raw))

    return public_key_sum


def sum_public_keys(pub_key1: ekt.PublicKey, pub_key2: ekt.PublicKey):


    pub_key1_as_tuple = decode_public_key(pub_key1.to_compressed_bytes())
    pub_key1_as_tuple = lift_x(pub_key1_as_tuple[0])

    if pub_key1_as_tuple is None:
        raise ValueError("Point at infinity cannot be added")

    pub_key2_as_tuple = decode_public_key(pub_key2.to_compressed_bytes())
    pub_key2_as_tuple = lift_x(pub_key2_as_tuple[0])

    if pub_key2_as_tuple is None:
        raise ValueError("Point at infinity cannot be added")

    # Check if one of the points is O
    if pub_key1_as_tuple is None:
        return pub_key2
    elif pub_key2_as_tuple is None:
        return pub_key1

    # Sum the public keys in Jacobian coordinates
    sum_pub_key_affine = fast_add(pub_key1_as_tuple, pub_key2_as_tuple)

    # Convert the raw public key to compressed bytes
    sum_pub_key_as_bytes = encode_raw_public_key(sum_pub_key_affine)
    print("sum_pub_key_as_bytes" , sum_pub_key_as_bytes.hex())

    # Convert the compressed bytes to a public key
    sum_pub_key = ekt.PublicKey(sum_pub_key_as_bytes)

    # Return the sum
    return sum_pub_key


def inv_point(pub_key):
    pub_key_as_tuple = decode_public_key(pub_key.to_compressed_bytes())

    if pub_key_as_tuple[1] == 0:
        raise ValueError("Point at infinity cannot be inverted")

    # inverse the public key
    # inv_pub_key_raw = (pub_key_as_tuple[0], pow(pub_key_as_tuple[1], SECPK1_P - 2, SECPK1_P))
    inv_pub_key_raw = (pub_key_as_tuple[0], (SECPK1_P - pub_key_as_tuple[1]) % SECPK1_P)
    

    # raw public key to compressed bytes
    inv_pub_key_as_bytes = encode_raw_public_key(inv_pub_key_raw)

    # compressed bytes to public key
    inv_pub_key = ekt.PublicKey(inv_pub_key_as_bytes)

    # return the inverse
    return inv_pub_key

def are_points_equal(pub_key1, pub_key2):
    pub_key1_as_tuple = decode_public_key(pub_key1.to_compressed_bytes())
    pub_key2_as_tuple = decode_public_key(pub_key2.to_compressed_bytes())

    if pub_key1_as_tuple[0] == pub_key2_as_tuple[0]:
        return True
    else:
        print("pub_key1_as_tuple[0] is: ", pub_key1_as_tuple[0])
        print("pub_key2_as_tuple[0] is: ", pub_key2_as_tuple[0])
        return False


def hash_to_pubkey(hash_str):
    # hash string to private key
    priv_key = hash_to_private_key(hash_str)

    # get the public key
    pub_key = priv_key.public_key
    print("in hash_to_pubkey the public key is: ", pub_key.to_compressed_bytes().hex())
    print("in hash_to_pubkey the public key type is: ", type(pub_key))
    # return the public key
    return pub_key



# Connect to the local node
w3 = w3.Web3(w3.HTTPProvider('http://127.0.0.1:8545'))

# Print the current block number
print("the current block number is: ", w3.eth.block_number)

# Print the current gas price
print("the current gas price is: ", w3.eth.gas_price)

# import account from private key string 0xecb9bf0998e95603b057a615c1eb972f88dbc365e5f0e8e20eda93cd74e1a542

key = "0xecb9bf0998e95603b057a615c1eb972f88dbc365e5f0e8e20eda93cd74e1a542"

# create PrivateKey object from key string
private_key = ekt.PrivateKey(bytes.fromhex(key[2:]))

# create account from private key
account = w3.eth.account.from_key(private_key)

# get public key from account
public_key = private_key.public_key

print("the public key from the hardcoded priv is: ", public_key.to_compressed_bytes().hex())

# Print the account address
print("the account address from the hardcoded priv is: ", account.address)

# Print the account balance
print("the account balance is: ", w3.eth.get_balance(account.address))


# # Create a simple transaction to 0x61c52BBc6a7E8910cf779DeF7Ec8aDEf8aB441B5 for 3 ether

# tx_hash = w3.eth.send_transaction({
#     'from': account.address,
#     'to': '0x61c52BBc6a7E8910cf779DeF7Ec8aDEf8aB441B5',
#     'value': w3.to_wei(3, 'ether'),
# })

# # Wait for the transaction to be mined, and get the transaction receipt
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# # Print the transaction receipt
# print("the transaction receipt is: ", tx_receipt)

# # Print the transaction receipt gas used
# print("the transaction receipt gas used is: ", tx_receipt.gasUsed)


# # print the new balance of the two accounts in ethers
# print("the new balance of the account is: ", w3.from_wei(w3.eth.get_balance(account.address), 'ether'))
# print("the new balance of the account is: ", w3.from_wei(w3.eth.get_balance('0x61c52BBc6a7E8910cf779DeF7Ec8aDEf8aB441B5'), 'ether'))



# create a message and hash it
message = "Hello World"
message_hash = hashlib.sha256(os.urandom(32))

## pad the message hash to 32 bytes
message_hash = message_hash.digest()



message_as_private_key = hash_to_private_key(message_hash.hex())

print("the message hash is: ", message_hash.hex())

# convert the hash to a curve point
message_point = hash_to_pubkey(message_hash.hex())
print("the message point is: ", message_point)



private_sum = sum_private_keys(private_key, message_as_private_key)
private_sum_as_public_key = private_sum.public_key

print("the private_sum as public key is: ", private_sum_as_public_key.to_compressed_bytes().hex())

public_key_sum = sum_public_keys(public_key, message_point)
public_key_sum2 = sum_public_keys2(public_key, message_point)

print("the public key sum is: ", public_key_sum.to_compressed_bytes().hex())
print("the public key sum is 2: ", public_key_sum2.to_compressed_bytes().hex())
print()
print("are the two sums (diff algo) equal? ", are_points_equal(public_key_sum, public_key_sum2))

print()
print("are the two public keys equal? (algo 1) ", are_points_equal(public_key_sum, private_sum_as_public_key))
print()
print("are the two public keys equal? (algo 2)", are_points_equal(public_key_sum2, private_sum_as_public_key))
# print("the inverse of the public key sum is: ", inv_point(public_key_sum).to_compressed_bytes().hex())


print("do the point and its inverse have the same x?", are_points_equal(public_key_sum, inv_point(public_key_sum)))
print("sum of public_key_sum and inverse of public_key_sum is: ", sum_public_keys(public_key_sum, inv_point(public_key_sum)).to_compressed_bytes().hex())
