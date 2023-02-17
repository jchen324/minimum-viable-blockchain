from Transaction import *
from Block import *
from Blockchain import *
from hashlib import sha256
from queue import Queue
from nacl.signing import VerifyKey
from nacl.encoding import Base64Encoder
import nacl.exceptions

class Node:
    def __init__(self, id = None):
        self.id = id
        self.other_nodes = []
        self.blockchain = Blockchain()
        self.block_queue = Queue()
        self.unverified_tx_pool : List[Transaction] = []
        self.valid_tx : List[Transaction] = []
        self.difficulty = 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    
    # check tx does not already exist on the blockchain
    def _tx_check_not_already_exist(self, tx: Transaction):
        curr = self.blockchain.last_block()
        while curr:
            if tx.tx_number == curr.currBlock.tx.tx_number:
                print("tx already exists")
                return False
            curr = curr.prevBlock
        return True
        
    # check 1: number hash is correct
    def _tx_check_hash_correct(self, tx: Transaction):
        input_list = tx.to_input_list()
        output_list = tx.to_output_list()

        transaction_data = json.dumps(input_list + output_list)

        transaction_hash = sha256(transaction_data.encode()).hexdigest()
        if transaction_hash != tx.tx_number:
            print("check 1 failed")
            return False
        return True


    def _tx_check_input_correct(self, tx: Transaction):

        first_pubkey = tx.input_list[0].output.pubkey

        # check if the key can verify the signature on this transaction
        signed = tx.sig.encode()
        sender_pubkey = VerifyKey(first_pubkey.encode(), encoder=Base64Encoder)
        try:
            sender_pubkey.verify(signed, encoder=Base64Encoder)
            # print(f"Transaction {target_tx.tx_number} signature is valid")
        except nacl.exceptions.BadSignatureError:
            print(f"Transaction {tx.tx_number} signature not valid")
            return False

        for input in tx.input_list:
            input_number = input.number
            input_output = input.output
            input_output_value = input_output.value
            input_output_pubkey = input_output.pubkey

            # check if each number in the input exists as a transaction already on the blockchain 
            found = False
            curr = self.blockchain.last_block()
            while curr:
                if input_number == curr.currBlock.tx.tx_number:
                    found = True
                    break
                curr = curr.prevBlock
            if (not found):
                print("tx input does not exist")
                return False
            
            # check if each output in the input actually exists in the named transaction,
            # and that public key is the most recent recipient of that output (i.e. not a double-spend)
            key = sha256((str(input_number) + str(input_output_pubkey) + str(input_output_value)).encode()).hexdigest()
            if (not (key in self.blockchain.UTXO)):
                print("input's output does not exist in UTXO/ double spending")
                return False
            
            # check if each output in the input has the same public key
            if first_pubkey != input_output_pubkey:
                print("diff pubkey for input's outputs")
                return False
            
        
        return True
        

    # check 3: the sum of the input and output values are equal
    def _tx_check_input_output_sum_correct(self, tx: Transaction):
        input_sum = 0
        output_sum = 0
        for input_tx in tx.input_list:
            input_sum += int(input_tx.output.value)
        for output_tx in tx.output_list:
            output_sum += int(output_tx.value)
        
        if (input_sum != output_sum): 
            print("check 3 failed")
        return (input_sum == output_sum)

    def check_valid_tx(self, tx: Transaction):
        return self._tx_check_not_already_exist(tx) and self._tx_check_hash_correct(tx) \
            and self._tx_check_input_correct(tx) and self._tx_check_input_output_sum_correct(tx)


    def mine_block(self, tx: Transaction):
        if self.check_valid_tx(tx):
            prevBlock = self.blockchain.last_block()
            prevHashing = prevBlock.currBlock.pow
            nonce = 0 # TODO
            pow = sha256((str(tx.to_dict()) + str(prevHashing) + str(nonce)).encode()).hexdigest()
            while int(pow, 16) > self.difficulty:
                nonce += 1
                pow = sha256((str(tx.to_dict()) + str(prevHashing) + str(nonce)).encode()).hexdigest()
            newBlock = Block(tx, prevHashing, str(nonce), pow)
            newLinkedBlock = LinkedBlock(prevBlock, newBlock, prevBlock.height + 1)
            self.blockchain.add_block(newLinkedBlock)
        else:
            print(f"Mining block: transaction not valid for transaction number {tx.tx_number}")
    
    def output_all_blocks(self):
        res = []
        curr = self.blockchain.last_block()
        while curr:
            res = [curr.currBlock.to_dict()] + res
            curr = curr.prevBlock
        with open("node_output.json", "w") as f:
            json.dump(res, f)

node = Node()
node.output_all_blocks()

def read_tx(filename):
    txs = []
    with open(f"./transactions/{filename}.json") as f:
        txs = json.load(f)
    return txs
        
txs = read_tx("Verified_Tx")
for tx in txs:
    tx_obj = Transaction(dict_obj=tx)
   
    node.mine_block(tx_obj)

node.output_all_blocks()



