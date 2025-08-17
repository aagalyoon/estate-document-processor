import asyncio
import unittest
from unittest import TestCase
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import MasterAgent, ClassificationAgent, ComplianceAgent
from models.document import Document
from utils.exceptions import ValidationError


class TestEdgeCases(TestCase):
    """Test edge cases and error conditions"""
    
    def setUp(self):
        self.master_agent = MasterAgent()
        self.classification_agent = ClassificationAgent()
        self.compliance_agent = ComplianceAgent()
    
    def test_empty_content_document(self):
        """Test handling of document with empty content"""
        payload = {
            "document_id": "EMPTY-001",
            "content": ""
        }
        
        with self.assertRaises(ValidationError):
            asyncio.run(self.master_agent.process(payload))
    
    def test_whitespace_only_content(self):
        """Test handling of document with only whitespace"""
        payload = {
            "document_id": "WHITESPACE-001",
            "content": "   \n\t\n   "
        }
        
        with self.assertRaises(ValidationError):
            asyncio.run(self.master_agent.process(payload))
    
    def test_mixed_category_document(self):
        """Test document with keywords from multiple categories"""
        content = """
        LAST WILL AND TESTAMENT and CERTIFICATE OF DEATH
        
        This document contains keywords from multiple categories.
        Date of Death: January 1, 2023
        Tax Year 2022
        Financial Statement
        Property Deed
        """
        
        payload = {
            "document_id": "MIXED-001",
            "content": content
        }
        
        result = asyncio.run(self.master_agent.process(payload))
        
        # Should classify to one category (likely Death Certificate due to strong keywords)
        self.assertIsNotNone(result.classification.category_code)
        self.assertGreater(result.classification.confidence, 0)
    
    def test_unicode_content(self):
        """Test handling of Unicode characters in content"""
        content = """
        Certificate of Death
        
        Name: José María González
        Date of Death: 死亡日期 January 1, 2023
        Location: München, Deutschland
        Special chars: €£¥ ™®© émoji 🎉
        """
        
        payload = {
            "document_id": "UNICODE-001",
            "content": content
        }
        
        result = asyncio.run(self.master_agent.process(payload))
        
        self.assertEqual(result.document_id, "UNICODE-001")
        self.assertEqual(result.status, "completed")
    
    def test_very_long_document(self):
        """Test handling of very long document"""
        # Create a long but valid document
        base_content = "Certificate of Death\nDate of Death: January 1, 2023\n"
        content = base_content + ("Additional content line.\n" * 1000)
        
        payload = {
            "document_id": "LONG-001",
            "content": content
        }
        
        result = asyncio.run(self.master_agent.process(payload))
        
        self.assertEqual(result.document_id, "LONG-001")
        self.assertEqual(result.classification.category_code, "01.0000-50")
    
    def test_special_characters_in_document_id(self):
        """Test document ID with special characters that should be rejected"""
        payload = {
            "document_id": "DOC@#$%",
            "content": "Valid content for testing"
        }
        
        with self.assertRaises(ValidationError):
            asyncio.run(self.master_agent.process(payload))
    
    def test_numeric_document_id(self):
        """Test numeric document ID (should work as string)"""
        payload = {
            "document_id": "12345",
            "content": "Certificate of Death - Valid content"
        }
        
        result = asyncio.run(self.master_agent.process(payload))
        self.assertEqual(result.document_id, "12345")
    
    def test_case_insensitive_classification(self):
        """Test that classification is case-insensitive"""
        contents = [
            "CERTIFICATE OF DEATH",
            "certificate of death",
            "Certificate Of Death",
            "CeRtIfIcAtE oF dEaTh"
        ]
        
        for i, content in enumerate(contents):
            full_content = f"{content}\nDate of Death: January 1, 2023"
            payload = {
                "document_id": f"CASE-{i}",
                "content": full_content
            }
            
            result = asyncio.run(self.master_agent.process(payload))
            self.assertEqual(result.classification.category_code, "01.0000-50",
                           f"Failed for content: {content}")
    
    def test_partial_keyword_matches(self):
        """Test document with partial keyword matches"""
        content = """
        This document mentions death but is not a certificate.
        It also mentions will but is not a will document.
        Financial information is present but not a statement.
        Tax information exists but not a tax return.
        """
        
        payload = {
            "document_id": "PARTIAL-001",
            "content": content
        }
        
        result = asyncio.run(self.master_agent.process(payload))
        
        # Should likely classify as Miscellaneous due to weak matches
        self.assertEqual(result.status, "completed")
        # Confidence should be relatively low
        self.assertLessEqual(result.classification.confidence, 0.5)
    
    def test_malformed_document_structure(self):
        """Test document with malformed structure but valid content"""
        content = "CertificateofDeathDateofDeathJanuary12023NameJohnDoe"
        
        payload = {
            "document_id": "MALFORMED-001",
            "content": content
        }
        
        result = asyncio.run(self.master_agent.process(payload))
        
        # Should still process but might not classify correctly
        self.assertEqual(result.status, "completed")
    
    def test_concurrent_processing(self):
        """Test concurrent processing of multiple documents"""
        payloads = [
            {
                "document_id": f"CONCURRENT-{i}",
                "content": f"Certificate of Death {i}\nDate of Death: January {i}, 2023"
            }
            for i in range(1, 6)
        ]
        
        async def process_all():
            tasks = [self.master_agent.process(p) for p in payloads]
            return await asyncio.gather(*tasks)
        
        results = asyncio.run(process_all())
        
        self.assertEqual(len(results), 5)
        for i, result in enumerate(results):
            self.assertEqual(result.document_id, f"CONCURRENT-{i+1}")
            self.assertEqual(result.status, "completed")


if __name__ == "__main__":
    unittest.main()