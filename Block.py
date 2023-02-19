from Transaction import *
from hashlib import sha256
import json

class Block:
    def __init__(self, tx: Transaction = None, prev = None, nonce = None, pow = None):
        self.tx = tx
        self.prev = prev
        self.nonce = nonce
        self.pow = pow

    def to_dict(self):
        dict_res = {
            "tx": self.tx.to_dict(),
            "prev": str(self.prev),
            "nonce": str(self.nonce),
            "pow": str(self.pow)
        }
        return dict_res

    def get_hash(self):
        return sha256(json.dumps(self.to_dict()).encode()).hexdigest()


class LinkedBlock:
    def __init__(self, prevBlock: Block, currBlock: Block, height):
        self.prevBlock = prevBlock
        self.currBlock = currBlock
        self.height = height
    
    @staticmethod
    def generate_genesis_linked_block():
        with open("./transactions/genesis_tx.json") as f:
            dict_obj = json.load(f)
            
        genesis_tx = Transaction(dict_obj=dict_obj)
        genesis_block = Block(genesis_tx, sha256(b'hello').hexdigest(), "0", sha256(b'world').hexdigest())
        genesis_linked_block = LinkedBlock(None, genesis_block, 1)
        return genesis_linked_block
        


