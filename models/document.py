from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentCategory(Enum):
    DEATH_CERTIFICATE = ("Death Certificate", "01.0000-50")
    WILL_OR_TRUST = ("Will or Trust", "02.0300-50")
    PROPERTY_DEED = ("Property Deed", "03.0090-00")
    FINANCIAL_STATEMENT = ("Financial Statement", "04.5000-00")
    TAX_DOCUMENT = ("Tax Document", "05.5000-70")
    MISCELLANEOUS = ("Miscellaneous", "00.0000-00")
    
    def __init__(self, display_name: str, code: str):
        self.display_name = display_name
        self.code = code


class Document(BaseModel):
    document_id: str = Field(description="Unique identifier for the document")
    content: str = Field(description="The raw content of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    uploaded_at: datetime = Field(default_factory=datetime.now)


class ClassificationResult(BaseModel):
    document_id: str
    category_code: str
    category_name: str
    confidence: float = Field(ge=0.0, le=1.0)


class ComplianceResult(BaseModel):
    document_id: str
    valid: bool
    reason: Optional[str] = None
    checks_performed: list[str] = Field(default_factory=list)


class ProcessingResult(BaseModel):
    document_id: str
    classification: ClassificationResult
    compliance: ComplianceResult
    status: str = Field(default="pending")
    processed_at: datetime = Field(default_factory=datetime.now)
    errors: list[str] = Field(default_factory=list)