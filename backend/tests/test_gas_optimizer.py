import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import time

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.chain import GasOptimizer, EthereumBlock

class TestGasOptimizer(unittest.TestCase):
    def setUp(self):
        self.optimizer = GasOptimizer()

    def test_initialization(self):
        self.assertEqual(self.optimizer.base_fee, 21000)
        self.assertEqual(self.optimizer.max_gas_limit, 30_000_000)

    def test_get_context_factor(self):
        # Context factor should be between 1.0 and 1.5 roughly based on the math
        # 1.0 + ( [0,1] * 0.5 )
        factor = self.optimizer.get_context_factor()
        self.assertGreaterEqual(factor, 1.0)
        self.assertLessEqual(factor, 1.5)

    def test_calculate_optimal_gas_empty_blocks(self):
        # Test with no recent blocks
        estimates = self.optimizer.calculate_optimal_gas([])
        
        # Check structure
        self.assertIn("safeLow", estimates)
        self.assertIn("standard", estimates)
        self.assertIn("fast", estimates)
        self.assertIn("congestion", estimates)
        
        # Check values relative to each other
        self.assertLess(estimates["safeLow"], estimates["standard"])
        self.assertGreater(estimates["fast"], estimates["standard"])
        
        # Default utilization is 0.5
        self.assertEqual(estimates["congestion"], 0.5)

    def test_calculate_optimal_gas_with_blocks(self):
        # Create dummy blocks
        blocks = []
        for i in range(5):
            # Block with high gas usage
            block = MagicMock(spec=EthereumBlock)
            block.gas_used = 25_000_000 # High usage
            blocks.append(block)
            
        estimates = self.optimizer.calculate_optimal_gas(blocks)
        
        # Utilization should be high approx 25/30 = 0.83
        self.assertGreater(estimates["congestion"], 0.8)
        
        # Should have applied congestion multiplier > 1.0
        # Base fee 21000 * 1.125 * context_factor
        # We can't know exact context_factor but we can check it's higher than base
        self.assertGreater(estimates["standard"], 21000)

if __name__ == '__main__':
    unittest.main()
