from Transaction import *
from Block import *
from hashlib import sha256
from typing import Dict
from typing import List

class Blockchain:
    def __init__(self):
        genesis = LinkedBlock.generate_genesis_linked_block()

        self.blockchain : List[LinkedBlock] = [genesis]
        self.UTXO: Dict[str, transaction_output] = {}

        tx = genesis.currBlock.tx
        self._add_to_UTXO(tx)
    
    def _add_to_UTXO(self, tx: Transaction):
        for o in tx.output_list:
            key = sha256((str(tx.tx_number) + str(o.pubkey) + str(o.value)).encode()).hexdigest()
            self.UTXO[key] = 1

    def _remove_from_UTXO(self, tx: Transaction):
        for i in tx.input_list:
            o = i.output
            key = sha256((str(i.number) + str(o.pubkey) + str(o.value)).encode()).hexdigest()
            self.UTXO.pop(key)
    
    def _remove_forked_tx_UTXO(self, tx: Transaction):
        for o in tx.output_list:
            key = sha256((str(tx.tx_number) + str(o.pubkey) + str(o.value)).encode()).hexdigest()
            self.UTXO.pop(key)
   

    def last_block(self):
        return self.blockchain[-1]

    def get_forking(self, node1: LinkedBlock, node2: LinkedBlock):
        node_1 = node1
        node_2 = node2
        if(not node_1 or not node_2):
            return None
        else:
            while node_1 != node_2:
                node_1 = node_1.prevBlock
                node_2 = node_2.prevBlock
                if (node_1 == node_2):
                    return node_1
                if (not node_1):
                    node_1 = node_2
                if (not node_2): 
                 node_2 = node_1
        return node_1

    # add a valid block to blockchain
    # check for forking 
    # add the block's output to UTXO and remove the block's input from UTXO
    def add_block(self, block: LinkedBlock):
        removed_tx_list = []
        oldBlock = self.last_block()
        self.blockchain.append(block)
        if (block.prevBlock != oldBlock and block.height > oldBlock.height):
            temp = oldBlock
            forkNode = self.get_forking(oldBlock, block)
            while temp != forkNode: 
                removed_tx_list.append(temp.currBlock.tx)
                self.blockchain.remove(temp)
                temp = temp.prevBlock
        self._add_to_UTXO(block.currBlock.tx)
        self._remove_from_UTXO(block.currBlock.tx)
        for tx in removed_tx_list:
            # remove the output of forked tx from UTXO since no longer be able to spend
            self._remove_forked_tx_UTXO(tx)
        return removed_tx_list
    

        







   

