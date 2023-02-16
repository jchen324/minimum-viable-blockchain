import json
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import Base64Encoder
import nacl.exceptions
from hashlib import sha256
import time

class Node:
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.mining_reward = 50
        self.difficulty = 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        self.valid_transactions = []
        self.address = nacl.signing.SigningKey.generate().verify_key
        self.verified_transactions_file = "verified_transactions.json"
        
    def read_transactions(self, filename):
        with open(filename, "r") as f:
            self.transactions = json.load(f)

    def verify_transaction(self, transaction):
        inputs = transaction["input"]
        outputs = transaction["output"]
        sender_pubkey_64 = inputs[0]["output"]["pubkey"]
        input_value = 0
        output_value = 0

        for i in inputs:
            input_number = i["number"]
            input_output = i["output"]

            # Find the transaction that input hash points to
            input_transaction = [tx for tx in self.chain if tx["number"] == input_number][0]
            
            # check 2.1: each number in the input exists as a transaction already on the blockchain
            if not input_transaction:
                return False
            
            # check 2.2: each output in the input actually exists in the named transaction
            matched = False
            for o in input_transaction["output"]:
                if o["pubkey"] == input_output["pubkey"] and o["value"] == input_output["value"]:
                    matched = True
            if not matched:
                return False
            
            # check 2.3: each output in the input has the same public key
            if input_output["pubkey"] != sender_pubkey_64: 
                return False
       
        for o in outputs:
            output_value += o["value"]

        # check 1: number hash is correct
        input_output_data = json.dumps(inputs + outputs)
        input_output_hash = sha256(input_output_data.encode()).hexdigest()
        if input_output_hash != transaction["number"]:
            return False

        # check 3: the sum of the input and output values are equal
        if (input_value != output_value):
            return False

        # check 2.3: the sender's key can verify the signature on this transaction
        signed = transaction["sig"].encode()
        sender_pubkey = VerifyKey(sender_pubkey_64.encode(), encoder=Base64Encoder)

        try:
            sender_pubkey.verify(signed, encoder=Base64Encoder)
            print(f"Transaction {transaction['number']} is valid")
            
        except nacl.exceptions.BadSignatureError:
            print(f"Transaction {transaction['number']} is invalid")
            return False
        
        return True
    
    def verify_transactions(self):
        self.valid_transactions = []
        with open(self.verified_transactions_file, "w") as f:
            for tx in self.transactions:
                if self.verify_transaction(tx):
                    self.valid_transactions.append(tx)
                    json.dump(tx, f)
                    f.write("\n")

    def mine_block(self):
        if not self.valid_transactions:
            return
        
        block_number = len(self.chain)
        block_reward = {"value": self.mining_reward, "pubkey": self.address.encode(encoder=nacl.encoding.HexEncoder).decode()}
        block_transactions = self.valid_transactions.copy()
        block_transactions.append({"number": sha256(json.dumps(block_reward).encode()).hexdigest(), "input": [], "output": [block_reward]})
        block_data = json.dumps({"number": block_number, "transactions": block_transactions, "previous_hash": self.chain[-1]["hash"] if self.chain else ""})
        
        while True:
            block_hash = sha256(block_data.encode()).hexdigest()
            if block_hash[:self.difficulty] == "0" * self.difficulty:
                print(f"Mined block {block_number} with hash: {block_hash}")
                self.chain.append({"number": block_number, "transactions": block_transactions, "hash": block_hash})
                self.transactions = []
                break

    def run_node(self):
        while True:
            self.read_transactions("transactions.json")
            self.verify_transactions()
            self.mine_block()
            time.sleep(5)

node = Node()
node.run_node()
