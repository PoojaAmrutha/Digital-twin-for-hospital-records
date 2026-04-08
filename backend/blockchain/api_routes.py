"""
Blockchain API Endpoints for HealthWatch AI
Polygon blockchain integration for medical records
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
import json

from database import get_db
from models import User, MedicalRecord
from blockchain.polygon_client import get_polygon_client

router = APIRouter(prefix="/api/blockchain", tags=["blockchain"])


@router.get("/status")
def get_blockchain_status():
    """Get Polygon blockchain connection status"""
    client = get_polygon_client()
    
    if not client:
        return {
            "connected": False,
            "message": "Blockchain client not initialized"
        }
    
    network_info = client.get_network_info()
    
    if client.account:
        network_info["balance"] = client.get_balance()
    
    return network_info


@router.post("/add-record")
def add_medical_record_to_blockchain(
    patient_id: int,
    record_data: dict,
    record_type: str = "general",
    db: Session = Depends(get_db)
):
    """
    Add a medical record to Polygon blockchain
    
    Args:
        patient_id: Patient's database ID
        record_data: Medical record data (will be hashed)
        record_type: Type of record (vital, prescription, diagnosis, etc.)
    """
    client = get_polygon_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Blockchain not configured")
    
    if not client.contract:
        raise HTTPException(status_code=503, detail="Smart contract not deployed")
    
    # Get patient
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Check if patient has Ethereum address
    if not patient.ethereum_address:
        raise HTTPException(
            status_code=400,
            detail="Patient does not have an Ethereum address. Please set one first."
        )
    
    try:
        # Add to blockchain
        result = client.add_medical_record(
            patient.ethereum_address,
            record_data,
            record_type
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=f"Blockchain transaction failed: {result.get('error')}"
            )
        
        return {
            "success": True,
            "message": "Record added to blockchain",
            "transaction_hash": result['transaction_hash'],
            "block_number": result['block_number'],
            "gas_used": result['gas_used'],
            "record_hash": result['record_hash'],
            "record_id": result.get('record_id'),
            "explorer_url": f"https://mumbai.polygonscan.com/tx/{result['transaction_hash']}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/record/{record_id}")
def get_blockchain_record(record_id: int):
    """Retrieve a medical record from Polygon blockchain"""
    client = get_polygon_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Blockchain not configured")
    
    record = client.get_record(record_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found on blockchain")
    
    return {
        "record": record,
        "explorer_url": f"https://mumbai.polygonscan.com/address/{client.contract.address}"
    }


@router.get("/patient/{patient_id}/records")
def get_patient_blockchain_records(patient_id: int, db: Session = Depends(get_db)):
    """Get all blockchain records for a patient"""
    client = get_polygon_client()
    
    if not client:
        raise HTTPException(status_code=503, detail="Blockchain not configured")
    
    # Get patient
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    if not patient.ethereum_address:
        return {
            "patient_id": patient_id,
            "ethereum_address": None,
            "record_count": 0,
            "record_ids": [],
            "message": "Patient does not have an Ethereum address"
        }
    
    # Get record IDs from blockchain
    record_ids = client.get_patient_records(patient.ethereum_address)
    record_count = client.get_patient_record_count(patient.ethereum_address)
    
    return {
        "patient_id": patient_id,
        "ethereum_address": patient.ethereum_address,
        "record_count": record_count,
        "record_ids": record_ids,
        "explorer_url": f"https://mumbai.polygonscan.com/address/{patient.ethereum_address}"
    }


@router.put("/patient/{patient_id}/ethereum-address")
def set_patient_ethereum_address(
    patient_id: int,
    ethereum_address: str,
    db: Session = Depends(get_db)
):
    """Set or update a patient's Ethereum/Polygon address"""
    # Validate address format
    if not ethereum_address.startswith('0x') or len(ethereum_address) != 42:
        raise HTTPException(
            status_code=400,
            detail="Invalid Ethereum address format. Must be 42 characters starting with 0x"
        )
    
    # Get patient
    patient = db.query(User).filter(User.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update address
    patient.ethereum_address = ethereum_address.lower()
    db.commit()
    db.refresh(patient)
    
    return {
        "success": True,
        "patient_id": patient_id,
        "ethereum_address": patient.ethereum_address,
        "message": "Ethereum address updated successfully"
    }


@router.get("/network-info")
def get_network_info():
    """Get detailed network information"""
    client = get_polygon_client()
    
    if not client:
        return {"error": "Blockchain not configured"}
    
    info = client.get_network_info()
    
    # Add gas price info
    if client.is_connected():
        try:
            gas_price_wei = client.w3.eth.gas_price
            gas_price_gwei = client.w3.from_wei(gas_price_wei, 'gwei')
            info["gas_price_gwei"] = float(gas_price_gwei)
            info["estimated_tx_cost_usd"] = float(gas_price_gwei) * 200000 / 1e9 * 0.85  # Rough estimate
        except:
            pass
    
    return info
