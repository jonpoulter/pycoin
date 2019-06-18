from uuid import uuid4

from blockchain import Blockchain
from utility.verification import Verification
from wallet import Wallet

class Node:

    def __init__(self):
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        """ Returns the user input (the recipient and transaction amount) as a tuple. """
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount = float(input('Your transaction amount please: '))
        return tx_recipient, tx_amount


    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input

    def print_options(self):
        print('Please choose')
        print('1: Add a new transaction value')
        print('2: Mine a new block')
        print('3: Output the blockchain blocks')
        print('4: Check transaction validity')
        print('5: Create Wallet')
        print('6: Load Wallet')
        print('7: Save Wallet')
        print('q: Quit')

    def print_blockchain_elements(self):
        #Output the blockchain list to the console
        #for index, block in enumerate(blockchain):
        for index in range(len(self.blockchain.get_chain())):
            print(f'Outputting block #{index}')
            #print(block)
            print(self.blockchain.get_chain()[index])
        else:
            print('-'*20)

    def listen_for_input(self):

        waiting_for_input = True

        while waiting_for_input:
            self.print_options()
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                # Add the transaction amount to the blockchain
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):
                    print('Added transaction')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                if not self.blockchain.mine_block():
                    print('Mining failed. Got no wallet with valid keys?')
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print('There are invalid transactions')
            elif user_choice == '5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == '7':
                self.wallet.save_keys()
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Option not recognised!')
            if not Verification.verify_chain(self.blockchain.get_chain()):
                print("***Invalid blockchain!***")
                break
            print(f'{self.wallet.public_key}\'s Balance is {self.blockchain.get_balance(self.wallet.public_key):6.2f}')
        else:
            #Loop is done - didn't break
            print('User Left!')

        print('Done!')


#Only run if the context of execution is CLI mode i.e. if this class is run directly and not imported.
if __name__ == '__main__':
    node = Node()
    node.listen_for_input()