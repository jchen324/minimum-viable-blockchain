# want to be able to generate transactions and create a json file 
import json
from typing import List
from nacl.encoding import Base64Encoder
from hashlib import sha256

# could be mutiple transactions so can think of it like a class so initalize all the fields
# what do we need when generating a Transaction 

class transaction_output:
    def __init__(self, value = None, pubkey = None, output_dict = None):
        # if the output_dict is not null 
        if output_dict:
            self.value = output_dict['value']
            self.pubkey = output_dict['pubkey']
            return
        self.value = value
        self.pubkey = pubkey

    # create the actual output list given the values 
    def to_dict(self):
        output_dict = {"value": self.value, "pubkey": self.pubkey}
        return output_dict
    

class transaction_input:
    def __init__(self, number = None, output : transaction_output = None, input_dict = None):
        # if the data is not empty ie not the genesis transaction 
        if input_dict:
            self.number = input_dict['number']
            # get the output data from the input dictionary object
            output_obj = input_dict['output']
            self.output = transaction_output(None, None, output_dict = output_obj)
            return
        self.number = number
        self.output = output
    
    def to_dict(self):
        number = str(self.number)
        value = str(self.output.value)
        pubkey = str(self.output.pubkey)
        input_dict =  {"number": number, "output": {"value": value, "pubkey": pubkey}}
        return input_dict


class Transaction: 
    def __init__(self, input_list : List[transaction_input] = [], output_list : List[transaction_output] = [], sig = None, dict_obj = None, genesis = False):
        # check if there is data in the object 
        if dict_obj:
            self._get_transaction(dict_obj)
            return
        self.input_list = input_list
        self.output_list = output_list
        self.sig = sig
        if (genesis):
            self.tx_number = "1"
        else: 
            self.tx_number = self.hashed_number()
            # print("1st hash :" + self.tx_number)
    
    def _get_transaction(self, dict_obj):
        try:
            self.tx_number = dict_obj['number']
            self.input_list = []
            self.output_list = []
            self.sig = dict_obj['sig']

            for input_tx in dict_obj['input']:
                input_transaction = transaction_input(input_dict=input_tx)
                self.input_list.append(input_transaction)
            

            for output_tx in dict_obj['output']:
                output_transaction = transaction_output(output_dict=output_tx)
                self.output_list.append(output_transaction)
        except:
            print("invalid transaction object")


    # return the transaction number
    def hashed_number(self):
        # get all the inputs and the outputs and the sig then hash it to get the number for the transaction
        input_list = self.to_input_list()
        output_list = self.to_output_list()
        transaction_data = json.dumps(input_list + output_list)
        transaction_hash = sha256(transaction_data.encode()).hexdigest()
        return transaction_hash
    

    # outputs the transaction in a dict object
    def to_dict(self):
        # should this not call hashed_number to get the hashed transaction number 
        dict = {"number" : self.tx_number} 
        dict["input"] = self.to_input_list()
        dict["output"] = self.to_output_list()
        dict['sig'] = self.sig
        return dict

    def to_input_list(self):
        inputList = []
        if (self.input_list):
            for input_tx in self.input_list:
                inputList.append(input_tx.to_dict())
        return inputList

    def to_output_list(self):
        outputList = []
        if (self.output_list):
            for output_tx in self.output_list:
                outputList.append(output_tx.to_dict())
        return outputList

        













    


