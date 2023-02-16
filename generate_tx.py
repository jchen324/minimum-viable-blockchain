import json
from nacl.signing import SigningKey
from nacl.signing import VerifyKey
from nacl.encoding import Base64Encoder
from hashlib import sha256
 
sk1 = SigningKey.generate()
pk1 = sk1.verify_key
print(str(pk1))

sk2 = SigningKey.generate()
pk2 = sk2.verify_key

sk3 = SigningKey.generate()
pk3 = sk3.verify_key

# Define the number of transactions to generate
num_transactions = 1

# Define the initial transaction number
transaction_number = 0

# Generate the transactions
transactions = []
for i in range(num_transactions):
    # Define the input and output fields for the transaction
    inputs = [{"number": "0", "output": {"value": 10, "pubkey": pk1.encode(encoder=Base64Encoder).decode()}}]
    outputs = [{"value": 10, "pubkey": pk2.encode(encoder=Base64Encoder).decode()}]

    # Serialize the transaction and compute its hash
    transaction_data = json.dumps(inputs + outputs)
    transaction_hash = sha256(transaction_data.encode()).hexdigest()

    # Sign the transaction hash with the sender's private key
    signed = sk1.sign(transaction_hash.encode(), encoder=Base64Encoder)

    # Add the signed transaction to the list of transactions
    transactions.append({"number": transaction_hash, "input": inputs, "output": outputs, "sig": signed.decode()})
    
    # Increment the transaction number for the next transaction
    transaction_number += 1

with open("transactions.json", "w") as f:
    json.dump(transactions, f)

