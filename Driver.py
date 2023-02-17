from Block import Block
from Blockchain import Blockchain
from Node import *
from Transaction import *
from threading import Thread
import random
from time import *
import json

class Driver:
    def __init__(self):
        self.nodes_list = []
        # list of dictionaries that can be iterated through
        self.unverified_Transactions : Transaction = []
        self.genesisBlock = Blockchain.createGenesisBlock(Blockchain)
        self.createThread(8)
        self.readTxfromJson()

    # create the multithread 
    def createThread(self, count):
        for id in range(1, count + 1):
            node = Node(self.genesisBlock, id)
            self.nodes_list.append(node)
            nodeThread = Thread(target=self.mining, args=(node,))
            nodeThread.start()
        for node in self.nodes_list:
            node.other_nodes += self.nodes_list

    def mining(self, node):
        
        

        node.writeToFile()

    def readTxfromJson(self):
        with open("transactions/Verified_Tx.json") as JsonFile:
            transaction_list = json.load(JsonFile)
        for tx in transaction_list:
            sleep(random.uniform(0, 1.0))
            self.unverified_Transactions.append(Transaction(dict_obj=tx))

    
if __name__ == "__main__":
    test = Driver()