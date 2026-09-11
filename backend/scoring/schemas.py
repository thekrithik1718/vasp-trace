from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# PROVISIONAL SCHEMAS
# These are internal schemas based on the conceptual input from Member 1.
# They are designed to be easily adapted once Member 1 provides the final integration contract.

class Transaction(BaseModel):
    from_address: str = Field(alias="from")
    to_address: str = Field(alias="to")
    amount: float
    timestamp: datetime
    tx_hash: str
    
    class Config:
        populate_by_name = True

class TransactionPath(BaseModel):
    addresses: List[str]
    transactions: List[Transaction]
    hop_count: int
    original_amount: float
    final_amount: float

class GraphInput(BaseModel):
    source_wallet: str
    paths: List[TransactionPath]

class ScoringResult(BaseModel):
    vasp_name: Optional[str]
    score: int = Field(ge=0, le=100)
    confidence_level: str  # e.g., "HIGH", "MEDIUM", "LOW"
    hop_count: int
    amount_retention: float
    supporting_path_count: int
    evidence: List[str]
