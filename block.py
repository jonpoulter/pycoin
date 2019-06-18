from time import time
from utility.printable import Printable

class Block(Printable):

    def __init__(self, block_height, previous_hash, transactions, proof, timestamp=None):
        self.block_height = block_height
        self.previous_hash = previous_hash
        self.timestamp = time() if timestamp is None else timestamp
        self.transactions = transactions
        self.proof = proof
