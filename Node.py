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
        self.other_nodes : List[Node] = []
        self.blockchain = Blockchain()
        self.block_queue = Queue()
        self.unverified_tx_pool : List[Transaction] = []
        self.alreadyMined : List[Transaction] = []
        self.difficulty = 0x07FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    
    # check tx does not already exist on the blockchain
    def _tx_check_not_already_exist(self, tx: Transaction):
        curr = self.blockchain.highest_block
        while curr:
            if tx.tx_number == curr.currBlock.tx.tx_number:
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
            return False
        return True


    def _tx_check_input_correct(self, tx: Transaction):
        first_pubkey = tx.input_list[0].output.pubkey

        # check if the key can verify the signature on this transaction
        signed = tx.sig.encode()
        sender_pubkey = VerifyKey(first_pubkey.encode(), encoder=Base64Encoder)
        try:
            sender_pubkey.verify(signed, encoder=Base64Encoder)
        except nacl.exceptions.BadSignatureError:
            return False

        for input in tx.input_list:
            input_number = input.number
            input_output = input.output
            input_output_value = input_output.value
            input_output_pubkey = input_output.pubkey

            # check if each number in the input exists as a transaction already on the blockchain 
            found = False
            curr = self.blockchain.highest_block
            i = 0
            while curr:
                if input_number == curr.currBlock.tx.tx_number:
                    found = True
                    break
                i = i + 1
                curr = curr.prevBlock
            if (not found):
                return False
            
            # check if each output in the input actually exists in the named transaction,
            # and that public key is the most recent recipient of that output (i.e. not a double-spend)
            key = sha256((str(input_number) + str(input_output_pubkey) + str(input_output_value)).encode()).hexdigest()
            if (not (key in self.blockchain.UTXO)):
                return False
            
            # check if each output in the input has the same public key
            if first_pubkey != input_output_pubkey:
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
        return (input_sum == output_sum)


    def check_valid_tx(self, tx: Transaction):
        return self._tx_check_not_already_exist(tx) and self._tx_check_hash_correct(tx) \
        and self._tx_check_input_correct(tx) and self._tx_check_input_output_sum_correct(tx)


    def mine_block(self, tx: Transaction):
        if self.check_valid_tx(tx):
            prevBlock = self.blockchain.highest_block
            prevHashing = prevBlock.currBlock.pow
            nonce = 0
            pow = sha256((str(tx.to_dict()) + str(prevHashing) + str(nonce)).encode()).hexdigest()

            # if pow is greater than difficulty, mine the block
            while int(pow, 16) > self.difficulty:
                nonce += 1
                pow = sha256((str(tx.to_dict()) + str(prevHashing) + str(nonce)).encode()).hexdigest()
            newBlock = Block(tx, prevHashing, str(nonce), pow)
            newLinkedBlock = LinkedBlock(prevBlock, newBlock, prevBlock.height + 1)
            self.blockchain.add_block(newLinkedBlock)
            
            # broadcast the mined block to other nodes
            self.broadcast_block(newBlock)
            return True
        else:
            return False
    
    def _verify_block_pow(self, block: Block):
        if int(block.pow, 16) > self.difficulty:
            return False
        if (sha256((str(block.tx.to_dict()) + str(block.prev) + str(block.nonce)).encode()).hexdigest() != block.pow):
            return False
        return True


    # add block broadcasted by other nodes to the blockchain
    def add_broadcasted_block(self):
        if self.block_queue.empty():
            return
        
        while not self.block_queue.empty():
            newBlock : Block = self.block_queue.get()
            if not (self._verify_block_pow(newBlock) and self.check_valid_tx(newBlock.tx)):
                continue
                
            # make sure the prev hash is on the blockchain
            targetBlock = None
            for linkedBlock in self.blockchain.blockchain:
                if linkedBlock.currBlock.pow == newBlock.prev:
                    targetBlock = linkedBlock
                    break
            if not targetBlock:
                continue
                
            newLinkedBlock = LinkedBlock(targetBlock.currBlock, newBlock, targetBlock.height + 1)
            res = self.blockchain.add_block(newLinkedBlock)

            # forking has occurred
            if (res["removed"]):
                for tx in res["removed"]:
                    self.unverified_tx_pool.append(tx)
                    self.alreadyMined.remove(tx)
            if (res["forked"]):
                for tx in res["forked"]:
                    self.unverified_tx_pool.remove(tx)
                    self.alreadyMined.append(tx)


    def broadcast_block(self, block: Block):
        for node in self.other_nodes:
            if node != self:
                node.block_queue.put(block)


    def output_all_blocks(self):
        res = []
        curr = self.blockchain.highest_block
        while curr:
            res = [curr.currBlock.to_dict()] + res
            curr = curr.prevBlock
        with open(f"outputs/node_output{self.id}.json", "w") as f:
            json.dump(res, f, indent=4)