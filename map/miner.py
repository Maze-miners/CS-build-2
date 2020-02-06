import hashlib
import requests
import json
import sys
from decouple import config
from functions import mine_coin

from uuid import uuid4

from timeit import default_timer as timer

url = config('API_URL')
key = config('API_KEY')

import random


def proof_of_work(last_proof):
    """
    Multi-Ouroboros of Work Algorithm
    - Find a number p' such that the last six digits of hash(p) are equal
    to the first six digits of hash(p')
    - IE:  last_hash: ...AE9123456, new hash 123456888...
    - p is the previous proof, and p' is the new proof
    - Use the same method to generate SHA-256 hashes as the examples in class
    """

    start = timer()

    print("Searching for next proof")
    proof = 0

    block_string = json.dumps(last_proof)
    while valid_proof(block_string, proof) is False:
        proof += 1

    print("Proof found: " + str(proof) + " in " + str(timer() - start))
    return proof


def valid_proof(last_hash, proof):
    """
    Validates the Proof:  Multi-ouroborus:  Do the last six characters of
    the hash of the last proof match the first six characters of the hash
    of the new proof?

    IE:  last_hash: ...AE9123456, new hash 123456E88...
    """
    # Hash the last proof
    last = f"{last_hash}".encode()
    last_hash_value = hashlib.sha256(last).hexdigest()

    # Get the last six characters of the last proof
    last_hash_values = last_hash_value[-6:]

    # Hash the current guess
    guess = f"{proof}".encode()
    guess_hash_value = hashlib.sha256(guess).hexdigest()

    # Get the first six characters of the guess proof
    guess_hash_values = guess_hash_value[:6]

    # Check the first six characters against the last
    return guess_hash_values == last_hash_values


def mine_for_coin():
    while True:
        # Get the last proof from the server
        get_proof = requests.get(
            f'{url}/api/bc/last_proof/',
            headers={
                "Authorization": f"Token {key}"
            }
        )
        # Get coin balance
        get_balance = requests.get(
            f'{url}/api/bc/get_balance/',
            headers={
                "Authorization": f"Token {key}"
            }
        )
        data = get_proof.json(), get_balance.json()
        new_proof = proof_of_work(data.get('proof'))

        post_data = {"proof": new_proof,
                     "id": id}

        r = requests.post({url} + "/mine", json=post_data)
        data = r.json()
        print(data)
        if data.get('message') == 'New Block Forged':
            coins_mined += 1
            print("Total coins mined: " + str(coins_mined))
        else:
            print(data.get('message'))
