from Block import Block
from Blockchain import Blockchain
from Node import *
from Transaction import *
from threading import Thread
import random
from time import *
from typing import List
import json
import time

class Driver:
    def __init__(self):
        self.nodes_list = []
        # list of dictionaries that can be iterated through
        self.global_unverified_tx : List[Transaction] = []
        self.createThread(8)
        self.readTxfromJson()

    # create the multithread 
    def createThread(self, count):
        for id in range(1, count + 1):
            node : Node = Node(id)
            self.nodes_list.append(node)
            nodeThread = Thread(target=self.mining, args=(node,))
            nodeThread.start()
        for node in self.nodes_list:
            node.other_nodes += self.nodes_list

    def mining(self, node: Node):
        while True:
            node.add_broadcasted_block()
            sleep(1)
            for transaction in self.global_unverified_tx:
                if transaction in node.alreadyMined or transaction in node.unverified_tx_pool:
                    continue
                node.unverified_tx_pool.append(transaction)
            if (node.unverified_tx_pool):
                tx = node.unverified_tx_pool[0]
                node.mine_block(tx) 
                node.alreadyMined.append(tx)
                node.unverified_tx_pool.remove(tx)
            
            if len(node.unverified_tx_pool) == 0:
                sleep(1)
                if len(node.unverified_tx_pool) == 0:
                    break
    
        node.output_all_blocks()

    def readTxfromJson(self):
        with open("transactions/Verified_Tx.json") as JsonFile:
            transaction_list = json.load(JsonFile)
        for tx in transaction_list:
            sleep(random.uniform(0, 0.5))
            self.global_unverified_tx.append(Transaction(dict_obj=tx))
    
if __name__ == "__main__":
    test = Driver()