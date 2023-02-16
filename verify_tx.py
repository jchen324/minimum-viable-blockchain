import json
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import Base64Encoder
import nacl.exceptions
from hashlib import sha256

# Load transactions from file
with open("transactions.json", "r") as f:
    transactions = json.load(f)

# Iterate through the transactions and verify each one
for transaction in transactions:
    # Extract the input, output, and signature fields from the transaction
    inputs = transaction["input"]
    outputs = transaction["output"]
    signed = transaction["sig"].encode()
    
    # Compute the hash of the input and output fields
    input_output_data = json.dumps(inputs + outputs)
    input_output_hash = sha256(input_output_data.encode()).hexdigest()
    if (input_output_hash != transaction["number"]):
        print(f"Transaction {transaction['number']} is invalid")
    
    # Get the public key of the sender from the input field
    sender_pubkey_64 = inputs[0]["output"]["pubkey"]
    sender_pubkey = VerifyKey(sender_pubkey_64.encode(), encoder=Base64Encoder)

    # Verify the signature of the transaction using the sender's public key
    try:
        sender_pubkey.verify(signed, encoder=Base64Encoder)
        print(f"Transaction {transaction['number']} is valid")
        
    except nacl.exceptions.BadSignatureError:
        print(f"Transaction {transaction['number']} is invalid")
