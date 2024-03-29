from flask import Flask, jsonify, request
from flask_cors import CORS

from wallet import Wallet
from blockchain import Blockchain

#initiate the Flask server passing in the execution context in which it is invoked
app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
#CORS(app)
def jsonify_block(block):
    dict_block = block.__dict__.copy()
    dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return dict_block

def jsonify_chain(chain):
    dict_chain = [block.__dict__.copy() for block in chain]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    return dict_chain

def jsonify_transactions(transactions):
    dict_transactions = [tx.__dict__ for tx in transactions]
    return dict_transactions

@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        #reset local blockchain with new keys
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance(wallet.public_key)
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving the keys failed'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        #reset local blockchain with loaded keys
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance(wallet.public_key)
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading the keys failed'
        }
        return jsonify(response), 500

@app.route('/balance', methods=['GET'])
def get_balance():
    if wallet.public_key != None:
        balance = blockchain.get_balance(wallet.public_key) 
        response = {
            'message': 'Fetched balance successfully',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Loading balance failed',
            'wallet_set_up': wallet.public_key != None
        }
        return jsonify(response), 400


@app.route('/', methods=['GET'])
def get_ui():
    return 'This works!'


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    payload = request.get_json()
    if not payload:
        response = {
            'message': 'No payload found'
        }
        return jsonify(response), 400

    required_fields = ['recipient', 'amount']
    if not all(field in payload for field in required_fields):
        response = {
            'message': 'Required data in payload is missing'
        }
        return jsonify(response), 400
    
    recipient = payload['recipient']
    amount = payload['amount']
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    success = blockchain.add_transaction(recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Successfully added transaction',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance(wallet.public_key)
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500


@app.route('/mine', methods=['POST'])
def mine():
    if blockchain.mine_block():
        response = {
            'message': 'Block added successfully',
            'block': jsonify_block(blockchain.get_last_blockchain_value()),
            'funds': blockchain.get_balance(wallet.public_key)
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding a block failed.',
            'wallet_setup_up': wallet.public_key != None
        }
        return jsonify(response), 500


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    transactions = blockchain.get_open_transactions()
    response = {
        'message': 'Fetched open transactions successfully',
        'transactions': jsonify_transactions(transactions)
    }
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    # chain_snapshot = blockchain.get_chain()
    # dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    # for dict_block in dict_chain:
    #     dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
    dict_chain = jsonify_chain(blockchain.get_chain())
    return jsonify(dict_chain), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


