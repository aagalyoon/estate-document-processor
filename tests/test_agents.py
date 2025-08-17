import asyncio
import unittest
from unittest import TestCase
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import MasterAgent, ClassificationAgent, ComplianceAgent
from data.mock_documents import MOCK_DOCUMENTS
from models.document import Document, DocumentCategory


class TestClassificationAgent(TestCase):
    def setUp(self):
        self.agent = ClassificationAgent()
    
    def test_death_certificate_classification(self):
        doc_data = MOCK_DOCUMENTS["death_certificate_valid"]
        payload = {"document": Document(**doc_data)}
        
        result = asyncio.run(self.agent.process(payload))
        
        self.assertEqual(result["category_code"], "01.0000-50")
        self.assertEqual(result["category_name"], "Death Certificate")
        self.assertGreater(result["confidence"], 0.5)
    
    def test_will_classification(self):
        doc_data = MOCK_DOCUMENTS["will_valid"]
        payload = {"document": Document(**doc_data)}
        
        result = asyncio.run(self.agent.process(payload))
        
        self.assertEqual(result["category_code"], "02.0300-50")
        self.assertEqual(result["category_name"], "Will or Trust")
        self.assertGreater(result["confidence"], 0.2)
    
    def test_miscellaneous_classification(self):
        doc_data = MOCK_DOCUMENTS["miscellaneous"]
        payload = {"document": Document(**doc_data)}
        
        result = asyncio.run(self.agent.process(payload))
        
        self.assertEqual(result["category_code"], "00.0000-00")
        self.assertEqual(result["category_name"], "Miscellaneous")


class TestComplianceAgent(TestCase):
    def setUp(self):
        self.agent = ComplianceAgent()
    
    def test_valid_death_certificate(self):
        doc_data = MOCK_DOCUMENTS["death_certificate_valid"]
        payload = {
            "document": Document(**doc_data),
            "category_code": "01.0000-50",
            "category_name": "Death Certificate"
        }
        
        result = asyncio.run(self.agent.process(payload))
        
        self.assertTrue(result["valid"])
        self.assertIn("All validation checks passed", result["reason"])
        self.assertGreater(len(result["checks_performed"]), 0)
    
    def test_invalid_death_certificate(self):
        doc_data = MOCK_DOCUMENTS["invalid_death_certificate"]
        payload = {
            "document": Document(**doc_data),
            "category_code": "01.0000-50",
            "category_name": "Death Certificate"
        }
        
        result = asyncio.run(self.agent.process(payload))
        
        self.assertFalse(result["valid"])
        self.assertIn("Validation failed", result["reason"])
    
    def test_valid_will(self):
        doc_data = MOCK_DOCUMENTS["will_valid"]
        payload = {
            "document": Document(**doc_data),
            "category_code": "02.0300-50",
            "category_name": "Will or Trust"
        }
        
        result = asyncio.run(self.agent.process(payload))
        
        self.assertTrue(result["valid"])
    
    def test_miscellaneous_bypass(self):
        doc_data = MOCK_DOCUMENTS["miscellaneous"]
        payload = {
            "document": Document(**doc_data),
            "category_code": "00.0000-00",
            "category_name": "Miscellaneous"
        }
        
        result = asyncio.run(self.agent.process(payload))
        
        self.assertTrue(result["valid"])
        self.assertIn("bypass", result["reason"].lower())


class TestMasterAgent(TestCase):
    def setUp(self):
        self.agent = MasterAgent()
    
    def test_full_pipeline_valid_death_certificate(self):
        doc_data = MOCK_DOCUMENTS["death_certificate_valid"]
        
        result = asyncio.run(self.agent.process(doc_data))
        
        self.assertEqual(result.document_id, "DOC-001")
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.classification.category_code, "01.0000-50")
        self.assertTrue(result.compliance.valid)
    
    def test_full_pipeline_invalid_will(self):
        doc_data = MOCK_DOCUMENTS["invalid_will"]
        
        result = asyncio.run(self.agent.process(doc_data))
        
        self.assertEqual(result.document_id, "DOC-007")
        self.assertEqual(result.status, "completed")
        # Invalid will gets classified as Miscellaneous and bypasses validation
        self.assertEqual(result.classification.category_code, "00.0000-00")
        self.assertTrue(result.compliance.valid)
    
    def test_full_pipeline_financial_statement(self):
        doc_data = MOCK_DOCUMENTS["financial_statement"]
        
        result = asyncio.run(self.agent.process(doc_data))
        
        self.assertEqual(result.document_id, "DOC-004")
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.classification.category_code, "04.5000-00")
        self.assertTrue(result.compliance.valid)
    
    def test_error_handling(self):
        invalid_payload = {"content": "Test content"}
        
        from utils.exceptions import ValidationError
        with self.assertRaises(ValidationError) as context:
            asyncio.run(self.agent.process(invalid_payload))
        
        self.assertIn("Document validation failed", str(context.exception))


if __name__ == "__main__":
    unittest.main()