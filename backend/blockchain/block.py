import hashlib
import json
from datetime import datetime

class Block:
    def __init__(self, index, data, previous_hash, timestamp=None):
        self.index = index
        self.timestamp = timestamp or datetime.now().isoformat()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_data = self.__dict__.copy()
        if "hash" in block_data:
            del block_data["hash"]
            
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        """
        Simple Proof of Work algorithm:
        Try different nonces until the hash starts with 'difficulty' zeros.
        """
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            # Recompute hash with new nonce
            # Note: We need to re-serialize because nonce is part of the dict
            # Efficient way (avoiding full re-dump if possible, but for safety re-dump):
            block_data = {
                "index": self.index,
                "timestamp": self.timestamp,
                "data": self.data,
                "previous_hash": self.previous_hash,
                "nonce": self.nonce
            }
            block_string = json.dumps(block_data, sort_keys=True)
            self.hash = hashlib.sha256(block_string.encode()).hexdigest()
