import time
import json
import hashlib
import random
from typing import List, Dict, Any

class EthereumBlock:
    def __init__(self, index: int, transactions: List[Dict], previous_hash: str):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
        
        # Ethereum specific fields (Simulated)
        self.gas_limit = 30_000_000
        self.gas_used = random.randint(21_000, 150_000)
        self.miner = f"0x{hashlib.sha256(str(random.random()).encode()).hexdigest()[:40]}"
        self.difficulty = 10_000_000 + random.randint(0, 5000)
        self.extra_data = "HealthWatch AI Audit Layer"

    def calculate_hash(self) -> str:
        """
        Calculate Keccak-256 style hash (using SHA3-256 for simulation accuracy)
        """
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        
        # Use SHA3-256 to mimic Keccak-256
        return "0x" + hashlib.sha3_256(block_string).hexdigest()

    def mine_block(self, difficulty: int):
        """
        Simulate Proof of Work mining
        """
        target = "0" * difficulty
        while not self.hash.startswith("0x" + target):
            self.nonce += 1
            self.hash = self.calculate_hash()

class GasOptimizer:
    """
    Context-Aware Gas Pricing (CAGP) Algorithm
    
    Dynamically adjusts gas prices based on:
    1. Network Congestion (Block utilization)
    2. Temporal Context (Peak vs Off-peak hours)
    3. Transaction Urgency (Priority fee)
    """
    def __init__(self):
        self.base_fee = 21000  # Standard ETH base fee
        self.max_gas_limit = 30_000_000
        self.target_gas_used = 15_000_000
    
    def get_context_factor(self) -> float:
        """
        Simulate context factor based on time of day
        Peak hours (9AM-5PM) have higher multiplier.
        """
        # In a real system, this would use datetime.now()
        # For simulation, we randomly drift it to show UI changes
        import math
        time_factor = (math.sin(time.time() / 10000) + 1) / 2 # Oscillate between 0 and 1
        return 1.0 + (time_factor * 0.5) # Multiplier 1.0x to 1.5x

    def calculate_optimal_gas(self, recent_blocks: List[EthereumBlock]) -> Dict[str, int]:
        """
        Calculate optimal gas fees using CAGP algorithm
        """
        context_factor = self.get_context_factor()
        
        # Analyze recent congestion
        if not recent_blocks:
            utilization = 0.5
        else:
            avg_gas = sum(b.gas_used for b in recent_blocks) / len(recent_blocks)
            utilization = avg_gas / self.max_gas_limit
            
        # EIP-1559 style adjustment with Context Multiplier
        congestion_multiplier = 1.0
        if utilization > 0.5:
            congestion_multiplier = 1.125 # Increase by 12.5%
        elif utilization < 0.5:
            congestion_multiplier = 0.875 # Decrease by 12.5%
            
        new_base_fee = int(self.base_fee * congestion_multiplier * context_factor)
        
        return {
            "safeLow": int(new_base_fee * 0.8),
            "standard": int(new_base_fee),
            "fast": int(new_base_fee * 1.2),
            "congestion": utilization
        }

class EthereumSim:
    """
    Simulated Ethereum Blockchain for Audit Logging
    Mimics Ethereum Mainnet behavior locally.
    """
    def __init__(self, difficulty=2):
        self.chain: List[EthereumBlock] = []
        self.difficulty = difficulty
        self.pending_transactions = []
        self.gas_optimizer = GasOptimizer() # CAGP Integration
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_tx = [{
            "from": "0x0000000000000000000000000000000000000000",
            "to": "0xHealthWatchGenesisContract",
            "value": 0,
            "data": "Genesis Block - HealthWatch AI Ethereum Audit Ledger"
        }]
        genesis_block = EthereumBlock(0, genesis_tx, "0x0000000000000000000000000000000000000000")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction: Dict):
        """
        Add a transaction to the mempool
        """
        # Enrich simulated tx
        if "hash" not in transaction:
            transaction["hash"] = "0x" + hashlib.sha3_256(json.dumps(transaction, sort_keys=True).encode()).hexdigest()
        
        # Apply CAGP for gas price forecast if not present
        if "gasPrice" not in transaction:
             estimates = self.gas_optimizer.calculate_optimal_gas(self.chain[-5:])
             transaction["gasPrice"] = estimates["standard"]
             
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address="0xHealthWatchMiner"):
        """
        Mine pending transactions into a new block
        """
        if not self.pending_transactions:
            return None
            
        new_block = EthereumBlock(
            len(self.chain),
            self.pending_transactions,
            self.last_block.hash
        )
        
        # Updates block with CAGP-optimized gas used
        estimates = self.gas_optimizer.calculate_optimal_gas(self.chain[-5:])
        tx_count = len(self.pending_transactions)
        base_gas = 21000 * tx_count
        # Add some random variance for data execution cost
        execution_gas = random.randint(0, 10000 * tx_count)
        new_block.gas_used = base_gas + execution_gas
        
        new_block.miner = miner_address
        new_block.mine_block(self.difficulty)
        
        self.chain.append(new_block)
        self.pending_transactions = [] # Clear mempool
        return new_block

    def is_chain_valid(self) -> bool:
        """
        Validate the entire chain integrity
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False
                
            if not current.hash.startswith("0x" + "0" * self.difficulty):
                return False

        return True

    def get_chain_data(self):
        """
        Return the chain data in a format suitable for API responses.
        Compatible with Ethereum data structures.
        """
        chain_data = []
        for block in self.chain:
            chain_data.append({
                "number": block.index,
                "hash": block.hash,
                "parentHash": block.previous_hash,
                "nonce": block.nonce,
                "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6...",
                "logsBloom": "0x00...",
                "transactionsRoot": "0x56e81f171bcc...",
                "stateRoot": "0xd5855eb08b3...",
                "miner": block.miner,
                "difficulty": block.difficulty,
                "totalDifficulty": block.difficulty * (block.index + 1),
                "extraData": block.extra_data,
                "size": random.randint(1000, 50000),
                "gasLimit": block.gas_limit,
                "gasUsed": block.gas_used,
                "timestamp": int(block.timestamp),
                "transactions": block.transactions,
                "uncles": []
            })
        return chain_data
