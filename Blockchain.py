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
        self.highest_block: LinkedBlock = self.blockchain[-1]
    
    def _add_to_UTXO(self, tx: Transaction):
        for o in tx.output_list:
            key = sha256((str(tx.tx_number) + str(o.pubkey) + str(o.value)).encode()).hexdigest()
            self.UTXO[key] = 1

    def _remove_from_UTXO(self, tx: Transaction):
        for i in tx.input_list:
            o = i.output
            key = sha256((str(i.number) + str(o.pubkey) + str(o.value)).encode()).hexdigest()
            self.UTXO.pop(key)
    
    # ensure all UTXOs are correct after forking
    def _reverse_forked_block_UTXO(self, tx: Transaction):
        for o in tx.output_list:
            key = sha256((str(tx.tx_number) + str(o.pubkey) + str(o.value)).encode()).hexdigest()
            self.UTXO.pop(key)
        for i in tx.input_list:
            o = i.output
            key = sha256((str(i.number) + str(o.pubkey) + str(o.value)).encode()).hexdigest()
            self.UTXO[key] = 1

    # return the most recent common block between two blockchains
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
        forked_tx_list = []

        oldBlock = self.highest_block
        self.blockchain.append(block)

        # forking case
        if (block.prevBlock != oldBlock and block.height > oldBlock.height):
            self.highest_block = self.blockchain[-1]
            temp = oldBlock
            forkNode = self.get_forking(oldBlock, block)

            # append all abandoned txs to remove_tx_list
            while temp != forkNode: 
                removed_tx_list.append(temp.currBlock.tx)
                temp = temp.prevBlock
            
            # remove the output of abandoned tx from UTXO and add input to UTXO
            for tx in removed_tx_list:
                self._reverse_forked_block_UTXO(tx)
            
            # integrate txs from the new chain to the blockchain
            temp2 = block
            while temp2 != forkNode:
                forked_tx_list.append(temp2.currBlock.tx)
            forked_tx_list.reverse()
            for tx in forked_tx_list:
                self._add_to_UTXO(tx)
                self._remove_from_UTXO(tx)

        # normal case 1: blockchain builds on the added block
        elif (block.prevBlock == oldBlock and block.height > oldBlock.height):
            self.highest_block = self.blockchain[-1]
            self._add_to_UTXO(block.currBlock.tx)
            self._remove_from_UTXO(block.currBlock.tx)
        
        # normal case 2: blockchain does not build on the added block
        elif (block.height <= oldBlock.height):
            pass
        
        return {"removed" : removed_tx_list, "forked": forked_tx_list}