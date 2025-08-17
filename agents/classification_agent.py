import re
from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent
from models.document import Document, DocumentCategory
import logging

logger = logging.getLogger(__name__)


class ClassificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ClassificationAgent",
            description="Classifies documents into estate-related categories based on content analysis"
        )
        self.keywords_map = self._initialize_keywords()
    
    def _initialize_keywords(self) -> Dict[DocumentCategory, List[str]]:
        return {
            DocumentCategory.DEATH_CERTIFICATE: [
                "certificate of death",
                "death certificate",
                "deceased",
                "date of death",
                "cause of death",
                "certifying physician",
                "funeral director",
                "vital statistics",
                "department of health"
            ],
            DocumentCategory.WILL_OR_TRUST: [
                "last will and testament",
                "trust agreement",
                "living trust",
                "revocable trust",
                "irrevocable trust",
                "testamentary",
                "executor",
                "trustee",
                "beneficiary",
                "bequeath",
                "estate planning"
            ],
            DocumentCategory.PROPERTY_DEED: [
                "property deed",
                "deed of trust",
                "warranty deed",
                "quitclaim deed",
                "real property",
                "parcel",
                "grantor",
                "grantee",
                "property description",
                "recording information"
            ],
            DocumentCategory.FINANCIAL_STATEMENT: [
                "financial statement",
                "bank statement",
                "investment account",
                "brokerage",
                "account balance",
                "portfolio",
                "assets",
                "liabilities",
                "net worth",
                "account summary"
            ],
            DocumentCategory.TAX_DOCUMENT: [
                "tax return",
                "form 1040",
                "w-2",
                "1099",
                "tax assessment",
                "irs",
                "internal revenue",
                "taxable income",
                "deductions",
                "tax liability"
            ]
        }
    
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            document = payload.get("document")
            if not document:
                raise ValueError("Missing document in payload")
            
            if isinstance(document, dict):
                document = Document(**document)
            
            category, confidence = self._classify_document(document.content)
            
            result = {
                "document_id": document.document_id,
                "category_code": category.code,
                "category_name": category.display_name,
                "confidence": confidence
            }
            
            self.log_processing(success=True)
            return result
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            self.log_processing(success=False)
            raise
    
    def _classify_document(self, content: str) -> Tuple[DocumentCategory, float]:
        content_lower = content.lower()
        
        scores = {}
        for category, keywords in self.keywords_map.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword in content_lower:
                    weight = len(keyword.split())
                    score += weight
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                score = score / len(keywords)
                scores[category] = score
                logger.debug(f"{category.display_name}: score={score:.2f}, matched={matched_keywords}")
        
        if not scores:
            return DocumentCategory.MISCELLANEOUS, 0.5
        
        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category] / 2.0, 1.0)
        
        confidence = max(0.3, confidence)
        
        return best_category, confidence
    
    def _extract_features(self, content: str) -> Dict[str, Any]:
        features = {
            "has_signature_block": bool(re.search(r"(signature|signed|witness)", content, re.I)),
            "has_date": bool(re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", content)),
            "has_ssn": bool(re.search(r"\d{3}-\d{2}-\d{4}", content)),
            "has_monetary_amount": bool(re.search(r"\$[\d,]+\.?\d*", content)),
            "document_length": len(content),
            "line_count": content.count("\n")
        }
        return features