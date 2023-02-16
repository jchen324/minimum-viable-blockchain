from Transaction import *
from Block import *
import json
from hashlib import sha256

output_list = [transaction_output(5, "111")]
tx = Transaction(1, [], output_list, sig="12312")
print(tx.to_dict())
print()
print(tx.to_output_list())
print()
print(tx.to_input_list())
print()

block = Block(tx, "123", "111", "yues")
print(block.get_hash())

with open("block.json", "w") as f:
    json.dump(block.to_dict(), f)

print(sha256(("1" + "2").encode()).hexdigest())
