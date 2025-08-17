import asyncio
from typing import Dict, Any, Optional
from .base_agent import BaseAgent
from .classification_agent import ClassificationAgent
from .compliance_agent import ComplianceAgent
from models.document import Document, ProcessingResult, ClassificationResult, ComplianceResult
import logging

logger = logging.getLogger(__name__)


class MasterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MasterAgent",
            description="Routes document processing tasks to appropriate specialized agents"
        )
        self.classification_agent = ClassificationAgent()
        self.compliance_agent = ComplianceAgent()
    
    async def process(self, payload: Dict[str, Any]) -> ProcessingResult:
        try:
            document = self._validate_payload(payload)
            
            logger.info(f"Processing document: {document.document_id}")
            
            classification_result = await self.classification_agent.process({
                "document": document
            })
            
            logger.info(f"Document classified as: {classification_result['category_name']} ({classification_result['category_code']})")
            
            compliance_payload = {
                "document": document,
                "category_code": classification_result["category_code"],
                "category_name": classification_result["category_name"]
            }
            compliance_result = await self.compliance_agent.process(compliance_payload)
            
            logger.info(f"Compliance check completed. Valid: {compliance_result['valid']}")
            
            result = ProcessingResult(
                document_id=document.document_id,
                classification=ClassificationResult(**classification_result),
                compliance=ComplianceResult(**compliance_result),
                status="completed"
            )
            
            self.log_processing(success=True)
            return result
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            self.log_processing(success=False)
            
            if 'document' in locals():
                return ProcessingResult(
                    document_id=document.document_id,
                    classification=ClassificationResult(
                        document_id=document.document_id,
                        category_code="00.0000-00",
                        category_name="Miscellaneous",
                        confidence=0.0
                    ),
                    compliance=ComplianceResult(
                        document_id=document.document_id,
                        valid=False,
                        reason=f"Processing error: {str(e)}"
                    ),
                    status="failed",
                    errors=[str(e)]
                )
            raise
    
    def _validate_payload(self, payload: Dict[str, Any]) -> Document:
        if "document_id" not in payload:
            raise ValueError("Missing required field: document_id")
        if "content" not in payload:
            raise ValueError("Missing required field: content")
        
        return Document(
            document_id=payload["document_id"],
            content=payload["content"],
            metadata=payload.get("metadata", {})
        )