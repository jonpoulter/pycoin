import hashlib as hl
import json

#define what is exported when using *
__all__ = ['hash_string_256', 'hash_block']

def hash_string_256(string):
    #produce 64 character hash of string
    return hl.sha256(string).hexdigest()

def hash_block(block):
    """ Hashes a block and returns a String representation of it

    Arguments:
        block:  The block that should be hashed
    """
    #must create a deep copy so hashable block refers to it's own copy for manipulation and not the one inside block.
    hashable_block = block.__dict__.copy()
    hashable_block['transactions'] = [tx.to_ordered_dict() for tx in hashable_block['transactions']]
    #we must sort the keys to ensure the dictionary produces the same json string everytime since dictionary does not guarantee order
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())