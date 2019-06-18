"""Provides verification helper methods."""

from utility.hash_util import hash_string_256, hash_block
from wallet import Wallet

class Verification:
    """A helper class which offers various static and class-based verification methods"""

    @classmethod
    def verify_chain(cls, blockchain):
        """ Verify the current blockchain and return True if it's valid, False if not valid """
        for index, block in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index-1]):
                return False
            # determine if hash is valid based on contents.  Need to remove reward transaction as this was not used when calculating the hash.
            if not cls.valid_proof(block.transactions[0:-1], block.previous_hash, block.proof):
                print('Proof of Work is invalid')
                return False
        
        return True

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        #This used when checking all open transactions in mempool so balance doesn't need to checked at this point.
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True):
        if check_funds == True:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)


    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        """Validate a proof of work number and see if it solves the puzzle

        Arguments:
            transactions: The transactions of the block for which the proof of work is calculated
            last_hash:  The previous block's hash which will be stored in this block
            proof:  The proof number we're verifying
        """
        #UTF8 Encode a stringified representation of the block
        guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
        #Create 64 hexadecimal character hash
        guess_hash = hash_string_256(guess)
        #guess_hash = hl.sha256(guess).hexdigest()
        print(guess_hash)
        return guess_hash[0:2] == '00'