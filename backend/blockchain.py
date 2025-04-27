import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask application
app = Flask(__name__)
CORS(app)

# Node identifier
node_identifier = str(uuid4()).replace('-', '')

class Blockchain:
    def __init__(self):
        self.chain = []  # Stores the blocks of the blockchain
        self.current_transactions = []  # Transactions awaiting to be added to a block
        self.nodes = set()  # Set of nodes in the blockchain network

        # Initialize the blockchain by creating the genesis block
        self.create_block(proof=100, previous_hash='1')

    def create_block(self, proof, previous_hash=None):
        """
        Creates a new block in the blockchain
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else '1',
        }

        # Reset current transactions
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to be added to the next block
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        """
        Hashes a block using SHA-256
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        """
        Implements the Proof of Work algorithm to find the next proof
        """
        proof = 0
        while not self.is_valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def is_valid_proof(last_proof, proof):
        """
        Validates the proof of work
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"  # Simple proof: first 4 characters of hash are zeros

    @property
    def last_block(self):
        """
        Returns the last block in the chain
        """
        return self.chain[-1] if self.chain else None


# Initialize the blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    """
    Mine a new block, solve proof of work, and reward the miner
    """
    last_block = blockchain.last_block
    last_proof = last_block['proof'] if last_block else 100
    proof = blockchain.proof_of_work(last_proof)

    # Reward for mining
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Add the new block to the blockchain
    previous_hash = blockchain.hash(last_block) if last_block else '1'
    block = blockchain.create_block(proof, previous_hash)

    response = {
        'message': 'New block mined',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Create a new transaction and add it to the current block
    """
    values = request.get_json()

    required_fields = ['sender', 'recipient', 'amount']
    if not values or not all(field in values for field in required_fields):
        return jsonify({'error': 'Missing values'}), 400

    # Create a new transaction
    index = blockchain.new_transaction(
        sender=values['sender'],
        recipient=values['recipient'],
        amount=values['amount']
    )

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Return the full blockchain
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    """
    Register new nodes to the blockchain network
    """
    values = request.get_json()

    nodes = values.get('nodes')
    if not nodes:
        return jsonify({'error': 'Please supply a valid list of nodes'}), 400

    for node in nodes:
        blockchain.nodes.add(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    """
    Resolve conflicts between nodes (not implemented in this version)
    """
    response = {
        'message': 'Consensus endpoint - logic not implemented',
        'chain': blockchain.chain,
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
