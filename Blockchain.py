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
   

    def last_block(self):
        return self.blockchain[-1]

    # add a valid block to blockchain
    # add the block's output to UTXO and remove the block's input from UTXO
    def add_block(self, block: LinkedBlock):
        self.blockchain.append(block)
        self._add_to_UTXO(block.currBlock.tx)
        self._remove_from_UTXO(block.currBlock.tx)
    
# test=Blockchain()

# with open("test.json", "w") as f:
#     json.dump(test.blockchain[0].currBlock.to_dict(), f)


        







   

