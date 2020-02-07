import hashlib
import requests
import json
import sys
from decouple import config
from map.functions import mine_coin, get_last_proof

from uuid import uuid4

from timeit import default_timer as timer

url = config('API_URL')
key = config('API_KEY')

import random


def proof_of_work(last_proof, difficulty):
    """
    Multi-Ouroboros of Work Algorithm
    - Find a number p' such that the last six digits of hash(p) are equal
    to the first six digits of hash(p')
    - IE:  last_hash: ...AE9123456, new hash 123456888...
    - p is the previous proof, and p' is the new proof
    - Use the same method to generate SHA-256 hashes as the examples in class
    """
    start = timer()

    print("\nSearching for next proof")
    proof = random.randint(0, 500000)

    block_string = json.dumps(last_proof)
    # will run until valid proof is found
    while valid_proof(block_string, difficulty, proof) is False:
        proof += 1

    print("\nProof found: " + str(proof) + " in " + str(timer() - start))
    return proof


def valid_proof(block_string, difficulty, proof):
    """
    Validates the Proof:  Multi-ouroborus:  Do the last six characters of
    the hash of the last proof match the first six characters of the hash
    of the new proof?

    IE:  last_hash: ...AE9123456, new hash 123456E88...
    """
    # Hash the current guess
    guess = f"{block_string}{proof}".encode()
    guess_hash_value = hashlib.sha256(guess).hexdigest()

    # Get the first n characters of the guess proof
    guess_hash_leading_zeroes = guess_hash_value[:difficulty]

    diff_str = '0' * difficulty

    # Check the guess hash for leading zeros
    return guess_hash_leading_zeroes == diff_str


def mine_for_coin():
    while True:
        # Get the last proof from the server
        print("\n...")
        last_proof = get_last_proof()
        
        new_proof = proof_of_work(last_proof["proof"], last_proof["difficulty"])
        coin = mine_coin(new_proof)
        return coin
