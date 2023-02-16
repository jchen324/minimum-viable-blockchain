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
            self.output = transaction_output(output_obj)
            return
        self.number = number
        self.output = output
    
    def to_dict(self):
        number = str(self.number)
        value = str(self.output.value)
        pubkey = str(self.output.pubkey)
        output_dict = {"number": number, "value": value, "pubkey": pubkey}
        return output_dict
    
class Transaction: 
    def __init__(self, tx_number = None, input_list : List[transaction_input] = None, output_list : List[transaction_output] = None, sig = None, dict_obj = None):
        # check if there is data in the object 
        if dict_obj:
            self._get_transaction(dict_obj)
            return
        self.tx_number = tx_number
        self.input_list = input_list
        self.output_list = output_list
        self.sig = sig 
    
    def _get_transaction(self, dict_obj):
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

    # find a better way for this function
    # def hashed_number(self):
    #     # get all the inputs and the outputs and the sig then hash it to get the number for the transaction
    #     number = []
    #     for input_tx in self.input_list:
    #         number.append(input_tx.convert())
    #     for output_tx in self.output_list:
    #         number.append(output_tx.convert())
    #     number.append(self.sig)
    #     return sha256(''.join(number).encode('utf-8')).hexdigest()
    
    # def toString(self):
    #     list_value = [str(self.tx_number)]
    #     for input_tx in self.input_list:
    #         list_value.append(input_tx.toString())
    #     for output_tx in self.output_list:
    #         list_value.append(output_tx.toString())
    #     list_value.append(self.sig)
    #     return ''.join(list_value)
    
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

        













    


