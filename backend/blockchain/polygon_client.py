"""
Polygon Blockchain Client for HealthWatch AI
Handles interaction with MedicalRecords smart contract on Polygon network
"""

from web3 import Web3
from eth_account import Account
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import hashlib

load_dotenv()

class PolygonClient:
    """Client for interacting with Polygon blockchain"""
    
    def __init__(self):
        # Connect to Polygon network
        rpc_url = os.getenv('POLYGON_RPC_URL', 'https://polygon-mumbai.g.alchemy.com/v2/demo')
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Load account from private key (if provided)
        private_key = os.getenv('POLYGON_PRIVATE_KEY')
        if private_key:
            self.account = Account.from_key(private_key)
        else:
            self.account = None
            print("⚠️ No private key found. Read-only mode.")
        
        # Load contract ABI
        abi_path = os.path.join(
            os.path.dirname(__file__),
            'contracts',
            'MedicalRecords_abi.json'
        )
        
        try:
            with open(abi_path, 'r') as f:
                self.contract_abi = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Contract ABI not found at {abi_path}")
            self.contract_abi = None
        
        # Load contract address
        contract_address = os.getenv('POLYGON_CONTRACT_ADDRESS')
        if contract_address and self.contract_abi:
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=self.contract_abi
            )
        else:
            self.contract = None
            print("⚠️ Contract not initialized. Set POLYGON_CONTRACT_ADDRESS in .env")
    
    def is_connected(self) -> bool:
        """Check if connected to Polygon network"""
        try:
            return self.w3.is_connected()
        except:
            return False
    
    def get_network_info(self) -> Dict:
        """Get current network information"""
        if not self.is_connected():
            return {"connected": False}
        
        try:
            chain_id = self.w3.eth.chain_id
            block_number = self.w3.eth.block_number
            
            # Determine network name
            network_names = {
                137: "Polygon Mainnet",
                80001: "Polygon Mumbai Testnet",
                1: "Ethereum Mainnet",
                11155111: "Sepolia Testnet"
            }
            
            return {
                "connected": True,
                "chain_id": chain_id,
                "network": network_names.get(chain_id, f"Unknown (Chain ID: {chain_id})"),
                "block_number": block_number,
                "account": self.account.address if self.account else None,
                "contract": self.contract.address if self.contract else None
            }
        except Exception as e:
            return {"connected": False, "error": str(e)}
    
    def create_record_hash(self, record_data: Dict) -> str:
        """Create a hash of medical record data"""
        # Sort keys for consistent hashing
        record_string = json.dumps(record_data, sort_keys=True)
        return hashlib.sha256(record_string.encode()).hexdigest()
    
    def add_medical_record(
        self,
        patient_address: str,
        record_data: Dict,
        record_type: str = "general"
    ) -> Dict:
        """
        Add a medical record to the blockchain
        
        Args:
            patient_address: Patient's Ethereum/Polygon address
            record_data: Medical record data (will be hashed)
            record_type: Type of record (vital, prescription, diagnosis, etc.)
        
        Returns:
            Transaction receipt with details
        """
        if not self.contract:
            raise Exception("Contract not initialized")
        
        if not self.account:
            raise Exception("No account configured. Cannot send transactions.")
        
        # Create hash of record data
        record_hash = self.create_record_hash(record_data)
        
        try:
            # Build transaction
            transaction = self.contract.functions.addRecord(
                Web3.to_checksum_address(patient_address),
                record_hash,
                record_type
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                self.account.key
            )
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            # Get record ID from event logs
            record_id = None
            if receipt['logs']:
                # Parse RecordAdded event
                event = self.contract.events.RecordAdded().process_receipt(receipt)
                if event:
                    record_id = event[0]['args']['id']
            
            return {
                'success': True,
                'transaction_hash': tx_hash.hex(),
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'record_hash': record_hash,
                'record_id': record_id,
                'status': 'confirmed' if receipt['status'] == 1 else 'failed'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_record(self, record_id: int) -> Optional[Dict]:
        """Retrieve a medical record from blockchain"""
        if not self.contract:
            raise Exception("Contract not initialized")
        
        try:
            record = self.contract.functions.getRecord(record_id).call()
            
            return {
                'id': record[0],
                'patient': record[1],
                'record_hash': record[2],
                'record_type': record[3],
                'timestamp': record[4],
                'added_by': record[5],
                'is_active': record[6]
            }
        except Exception as e:
            return None
    
    def get_patient_records(self, patient_address: str) -> List[int]:
        """Get all record IDs for a patient"""
        if not self.contract:
            raise Exception("Contract not initialized")
        
        try:
            record_ids = self.contract.functions.getPatientRecords(
                Web3.to_checksum_address(patient_address)
            ).call()
            return list(record_ids)
        except Exception as e:
            return []
    
    def get_patient_record_count(self, patient_address: str) -> int:
        """Get total number of records for a patient"""
        if not self.contract:
            return 0
        
        try:
            count = self.contract.functions.getPatientRecordCount(
                Web3.to_checksum_address(patient_address)
            ).call()
            return count
        except:
            return 0
    
    def is_authorized_provider(self, provider_address: str) -> bool:
        """Check if an address is an authorized healthcare provider"""
        if not self.contract:
            return False
        
        try:
            return self.contract.functions.isAuthorizedProvider(
                Web3.to_checksum_address(provider_address)
            ).call()
        except:
            return False
    
    def get_balance(self, address: Optional[str] = None) -> float:
        """Get MATIC balance of an address"""
        if not self.is_connected():
            return 0.0
        
        addr = address or (self.account.address if self.account else None)
        if not addr:
            return 0.0
        
        try:
            balance_wei = self.w3.eth.get_balance(Web3.to_checksum_address(addr))
            return float(self.w3.from_wei(balance_wei, 'ether'))
        except:
            return 0.0


# Singleton instance
_polygon_client = None

def get_polygon_client() -> Optional[PolygonClient]:
    """Get or create Polygon client instance"""
    global _polygon_client
    
    if _polygon_client is None:
        try:
            _polygon_client = PolygonClient()
            if not _polygon_client.is_connected():
                print("⚠️ Polygon client created but not connected")
        except Exception as e:
            print(f"❌ Failed to create Polygon client: {e}")
            return None
    
    return _polygon_client
