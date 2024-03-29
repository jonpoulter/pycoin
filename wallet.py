from Crypto.PublicKey import RSA
import Crypto.Random
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import binascii

class Wallet:

    def __init__(self):
        self.private_key = None
        self.public_key = None

    
    def create_keys(self):
        self.private_key, self.public_key = self.generate_keys()


    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open('wallet.txt', mode='w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
                return True
            except (IOError, IndexError):
                print('Saving wallet failed.')
                return False


    def load_keys(self):
        try:
            with open('wallet.txt', mode='r') as f:
                self.public_key = f.readline()[:-1]
                self.private_key = f.readline()
            return True
        except (IOError, IndexError):
            print('Loading wallet failed.')
            return False
    

    def generate_keys(self):
        """Generates a tuple of (private_key, public_key) in ASCII format"""
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii'))

    
    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.importKey(binascii.unhexlify(self.private_key)))
        hashed_transaction = SHA256.new((str(sender) + str(recipient) + str(amount)).encode('utf8'))
        signature = signer.sign(hashed_transaction)
        return binascii.hexlify(signature).decode('ascii')


    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        hashed_transaction = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode('utf8'))
        return verifier.verify(hashed_transaction, binascii.unhexlify(transaction.signature))