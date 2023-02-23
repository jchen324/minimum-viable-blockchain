# minimum-viable-blockchain
## Description
This is a simulation of a "Minimum Viable Blockchain" (MVB), a simplified version of the technology underlying Bitcoin. The MVB has nodes which validate transactions, perform proofs of work, and communicate in order to process transactions. It also emulates the mining and transaction verification process of Bitcoin.

The MVB has implemented the following:
- Authentic transactions that are resistant to theft
- Open competition amongst nodes to validate transactions
- Detection of double spending
- Use of proof-of-work to raise the cost of running attacks against the network
- Detection of and reaction to forks in the chain

Rather than communicating over a network, the simulated nodes run in threads. Transactions, either valid or intentionally invalid, are defined in a file which is read by the simulation and provided to the nodes. The threading is non-cooperative, which is to say that there are no synchronization primitives such as locks. This simulates nodes running independent of one another.

## How to Run
After installing all the dependencies listed in ```requirements.txt```, simply run ```python3 Driver.py``` to run the simulation.

## Other Details 
Please refer to this [link](https://github.com/PratyushRT/blockchainsS23/wiki/Assignment-1) for more details.