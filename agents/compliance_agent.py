import re
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from models.document import Document
import logging

logger = logging.getLogger(__name__)


class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ComplianceAgent",
            description="Validates documents based on category-specific compliance rules"
        )
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_validation_rules(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "01.0000-50": [
                {
                    "name": "contains_certificate_title",
                    "check": lambda content: "certificate of death" in content.lower(),
                    "error": "Must contain 'Certificate of Death'"
                },
                {
                    "name": "has_date_of_death",
                    "check": lambda content: bool(re.search(r"date of death", content, re.I)),
                    "error": "Must have 'Date of Death' field"
                },
                {
                    "name": "has_deceased_name",
                    "check": lambda content: bool(re.search(r"(name of deceased|full name|deceased)", content, re.I)),
                    "error": "Must include deceased person's name"
                },
                {
                    "name": "has_certificate_number",
                    "check": lambda content: bool(re.search(r"(certificate number|cert\.?\s*no\.?|registration)", content, re.I)),
                    "error": "Must have certificate number"
                }
            ],
            "02.0300-50": [
                {
                    "name": "contains_will_or_trust",
                    "check": lambda content: any(term in content.lower() for term in ["last will and testament", "trust agreement", "living trust", "revocable trust"]),
                    "error": "Must contain 'Last Will and Testament' or 'Trust Agreement'"
                },
                {
                    "name": "has_testator_or_grantor",
                    "check": lambda content: bool(re.search(r"(testator|grantor|settlor|trustor)", content, re.I)),
                    "error": "Must identify the testator or grantor"
                },
                {
                    "name": "has_beneficiary_info",
                    "check": lambda content: bool(re.search(r"(beneficiary|beneficiaries|heir|inherit)", content, re.I)),
                    "error": "Must include beneficiary information"
                }
            ],
            "03.0090-00": [
                {
                    "name": "contains_deed_type",
                    "check": lambda content: bool(re.search(r"(warranty deed|quitclaim deed|deed of trust|property deed)", content, re.I)),
                    "error": "Must specify deed type"
                },
                {
                    "name": "has_property_description",
                    "check": lambda content: bool(re.search(r"(property description|parcel|lot|legal description)", content, re.I)),
                    "error": "Must include property description"
                }
            ],
            "04.5000-00": [
                {
                    "name": "contains_financial_info",
                    "check": lambda content: bool(re.search(r"(account|balance|statement|financial)", content, re.I)),
                    "error": "Must contain financial account information"
                },
                {
                    "name": "has_monetary_amounts",
                    "check": lambda content: bool(re.search(r"\$[\d,]+\.?\d*", content)),
                    "error": "Must include monetary amounts"
                }
            ],
            "05.5000-70": [
                {
                    "name": "contains_tax_info",
                    "check": lambda content: bool(re.search(r"(tax|irs|internal revenue|form \d+|schedule)", content, re.I)),
                    "error": "Must contain tax-related information"
                },
                {
                    "name": "has_tax_year",
                    "check": lambda content: bool(re.search(r"(tax year|year \d{4}|20\d{2})", content, re.I)),
                    "error": "Must specify tax year"
                }
            ]
        }
    
    async def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.start_processing()
        try:
            document = payload.get("document")
            category_code = payload.get("category_code")
            category_name = payload.get("category_name", "Unknown")
            
            if not document or not category_code:
                raise ValueError("Missing required fields: document and category_code")
            
            if isinstance(document, dict):
                document = Document(**document)
            
            valid, reason, checks = self._validate_document(document.content, category_code)
            
            result = {
                "document_id": document.document_id,
                "valid": valid,
                "reason": reason,
                "checks_performed": checks
            }
            
            logger.info(f"Compliance check for {category_name} document {document.document_id}: {'PASSED' if valid else 'FAILED'}")
            if not valid:
                logger.warning(f"Validation failure reason: {reason}")
            
            self.log_processing(success=True)
            return result
            
        except Exception as e:
            logger.error(f"Compliance validation error: {str(e)}")
            self.log_processing(success=False)
            raise
    
    def _validate_document(self, content: str, category_code: str) -> tuple[bool, Optional[str], List[str]]:
        checks_performed = []
        
        if category_code == "00.0000-00":
            return True, "Miscellaneous documents bypass validation", ["no_validation_required"]
        
        rules = self.validation_rules.get(category_code, [])
        
        if not rules:
            logger.info(f"No specific validation rules for category {category_code}, bypassing validation")
            return True, f"No validation rules defined for category {category_code}", ["validation_bypassed"]
        
        failed_checks = []
        for rule in rules:
            check_name = rule["name"]
            checks_performed.append(check_name)
            
            try:
                if not rule["check"](content):
                    failed_checks.append(rule["error"])
                    logger.debug(f"Check '{check_name}' failed: {rule['error']}")
            except Exception as e:
                logger.error(f"Error executing check '{check_name}': {str(e)}")
                failed_checks.append(f"Check '{check_name}' failed with error")
        
        if failed_checks:
            reason = "Validation failed: " + "; ".join(failed_checks)
            return False, reason, checks_performed
        
        return True, "All validation checks passed", checks_performed