from ecdsa.curves import SECP256k1
from ecdsa.ellipticcurve import Point
from ecdsa.keys import SigningKey, VerifyingKey
from hashlib import sha256


curve = SECP256k1.curve
n = SECP256k1.order

def is_hex_string(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False

def double_sha256(x):
    x1 = sha256(x).digest()
    return sha256(x1)

def get_verkey_x_as_number(verkey):
    x_as_bytes = verkey.to_string('raw')[0:32]
    x_as_number = int(x_as_bytes.hex(),16)
    return x_as_number

def get_verkey_y_as_number(verkey):
    y_as_bytes = verkey.to_string('raw')[32:64]
    y_as_number = int(y_as_bytes.hex(),16)
    return y_as_number

def verkey_to_point(verkey):
    x = get_verkey_x_as_number(verkey)
    y = get_verkey_y_as_number(verkey)
    curve = verkey.curve
    p = curve.curve.p()
    return Point(curve.curve, x%p, y%p)

def point_to_verkey(point):
    x = point.x()
    y = point.y()
    curve = point.curve()
    point_as_hex = hex(x)[2:] + hex(y)[2:]
    point_as_bytes = bytes.fromhex(point_as_hex)
    return VerifyingKey.form_string(point_as_bytes, SECP256k1, double_sha256)

def hash_to_privkey(hash_string):
    hash_as_number = 0

    if is_hex_string(hash_string):
        hash_as_number = int(hash_string, 16) % n
    elif isinstance(hash_string, bytes):
        hash_as_number = int(hash_string.hex(), 16) % n
    else:
        raise TypeError("hash_string must be either bytes or hex")
    return SigningKey.from_secret_exponent(hash_as_number, SECP256k1, hashfunc = double_sha256)

if __name__ == "__main__":

    # priv key
    private_key_alice = SigningKey.generate(curve=SECP256k1)
    private_key_bob = SigningKey.generate(curve=SECP256k1)
    print(f"Private key Alice: {private_key_alice.to_string().hex()}")
    print(f"Secret multiplier of private key Alice: {private_key_alice.privkey.secret_multiplier}")
    print(f"Private key Bob: {private_key_bob.to_string().hex()}")
    print(f"Secret multiplier of private key Bob: {private_key_bob.privkey.secret_multiplier}")

    print()
    # add them
    sum_of_multipliers = (private_key_alice.privkey.secret_multiplier +
                          private_key_bob.privkey.secret_multiplier) % n
    # get pubkey
    new_private_key = SigningKey.from_secret_exponent(sum_of_multipliers, SECP256k1, hashfunc = double_sha256)
    print(f"Private key New: {new_private_key.to_string().hex()}")
    print(f"Secret multiplier of private key New: {new_private_key.privkey.secret_multiplier}")
    # get point
    new_public_key = new_private_key.verifying_key
    new_public_key_point = verkey_to_point(new_public_key)

    print()

    #pubkey
    public_key_alice = private_key_alice.verifying_key
    public_key_bob = private_key_bob.verifying_key
    print(f"Public key curve: {public_key_alice.curve}")
    print(f"Public key Alice compressed: {public_key_alice.to_string('compressed').hex()}")
    print(f"Public key Bob: {public_key_bob.to_string('compressed').hex()}")
    # pubkey points
    public_key_alice_as_point = verkey_to_point(public_key_alice)
    public_key_bob_as_point = verkey_to_point(public_key_bob)
    # add them
    sum_point = public_key_alice_as_point + public_key_bob_as_point
    print(f"sum point x = {sum_point.x()}")
    print(f"sum point y = {sum_point.y()}")
    # get point
    print(f"are the two keys equal? {sum_point == new_public_key_point}")


    # point eq?



