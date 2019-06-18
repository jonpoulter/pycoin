from functools import reduce
import hashlib as hl
import json
import pickle

from block import Block
from transaction import Transaction
#use our utility module
from utility.hash_util import hash_block
from utility.verification import Verification
from wallet import Wallet

#Global scope
#Initializing out blockchain with genesis block

#The reward we give to miners
MINING_REWARD = 10

#First block added to chain
GENESIS_BLOCK = Block(0, '', [], 100, 0)


class Blockchain:

    def __init__(self, node):
        #Initializing the blockchain
        self.__chain = [GENESIS_BLOCK]
        #Unhandled transactions sitting in 'mempool'
        self.__open_transactions = []
        #load data at start up
        self.load_data()
        self.hosting_node = node

    def get_chain(self):
        return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def save_data(self):
        try:
            #overwrite file with new snapshot of blockchain
            with open('blockchain.txt', 'w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.block_height, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                f.write(json.dumps(saveable_tx))
        except IOError:
            print('Saving failed!')


    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                #de-serialize json object minus \n
                blockchain =json.loads(file_content[0][:-1])
                open_transactions = json.loads(file_content[1])

                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
                    #Created OrderDict for transactions rather than the default Dict
                    # converted_tx = [OrderedDict([
                    #                              ('sender', tx['sender']),
                    #                              ('recipient', tx['recipient']),
                    #                              ('amount', tx['amount'])
                    #                             ]) for tx in block['transactions']]
                    updated_block = Block(block['block_height'], 
                                        block['previous_hash'], 
                                        converted_tx,
                                        block['proof'],
                                        block['timestamp'])
                
                    updated_blockchain.append(updated_block)

                self.__chain = updated_blockchain
                
                updated_transactions = []

                for tx in open_transactions:
                    updated_tx = Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    #Create OrderDict for open transactions rather than the default Dict
                    # updated_tx = OrderedDict([
                    #     ('sender', tx['sender']),
                    #     ('recipient', tx['recipient']),
                    #     ('amount', tx['amount'])
                    # ])
                    updated_transactions.append(updated_tx)

                self.__open_transactions = updated_transactions

        except (IOError,IndexError):
           #In case no file exists or genesis block doesn't exist.  These issues are self-healing as Blockchain constructor initializes chain.
           pass

    def save_data_bin(self):
        try:
            with open('blockchain.bin', 'wb') as f:
                #define pickle schema
                saved_data = {
                    "chain": blockchain,
                    "ot": open_transactions
                }
                f.write(pickle.dumps(saved_data))
        except IOError:
            print('Saving failed!')


    def load_data_bin(self):
        try:
            with open('blockchain.bin', 'rb') as f:
                saved_data = pickle.loads(f.read())
                global blockchain, open_transactions
                blockchain = saved_data['chain']
                open_transactions = saved_data['ot']
        except IOError:
            print('File not found!')
        finally:
            print('Clean up!')


    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while Verification.valid_proof(self.__open_transactions, last_hash, proof) == False:
            proof += 1
        return proof


    def get_balance(self, participant):
        """ Calculate and return the balance of a participant

        Arguments:
            participant:  The participant whose balance is returned.
        """
        #nested list comprehension
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__chain]
        
        #use of reduce function
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum+sum(tx_amt) if len(tx_amt) > 0 else tx_sum,
                                    tx_sender,
                                    0)
        #amount_sent = 0
        #for tx in tx_sender:
        #    if len(tx) > 0:
        #        amount_sent += tx[0]
        amount_received = 0
        for tx in tx_recipient:
            if len(tx) > 0:
                amount_received += sum(tx)
        return amount_received - amount_sent


    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, signature, amount=1.0):
        """ Append a new value as well as the last blockchain value to the blockchain 
        
        Arguments:
            recipient: The recipient of the coins
            sender: The sender of the coins (default = owner)
            signature:  the signed transaction using the sender's private key
            amount: The amount of coins sent with the transaction (default = 1.0)
        """

        if self.hosting_node == None:
            return False
        transaction = Transaction(sender, recipient, signature, amount)
        
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            #save open transaction changes
            self.save_data()
            return True
        return False

    def mine_block(self):
        """Create a new block and add open transactions to it"""
        
        if self.hosting_node == None:
            return False
        last_block = self.__chain[-1]
        hashed_block = hash_block(last_block)
        #calculate nonce for new block
        proof = self.proof_of_work()

        copied_transactions = self.__open_transactions[:]

        #Verify all transactions are valid before progessing to mining.
        if all([Wallet.verify_transaction(tx) for tx in copied_transactions]) == False:
           return False

        #No need to sign a reward transaction as this is baked into the protocol
        reward_transaction = Transaction('MINING', self.hosting_node, '', MINING_REWARD)
        copied_transactions.append(reward_transaction)    
        block = Block(len(self.__chain), hashed_block, copied_transactions, proof, None)
        
        self.__chain.append(block)
        self.__open_transactions = []
        #save blockchain changes 
        self.save_data()
        return True




