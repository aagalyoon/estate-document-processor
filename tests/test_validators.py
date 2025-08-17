import unittest
from unittest import TestCase
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import DocumentValidator
from utils.exceptions import ValidationError


class TestDocumentValidator(TestCase):
    
    def test_valid_payload(self):
        """Test validation with a valid payload"""
        payload = {
            "document_id": "DOC-123",
            "content": "This is valid document content for testing purposes."
        }
        # Should not raise any exception
        DocumentValidator.validate_payload(payload)
    
    def test_missing_document_id(self):
        """Test validation with missing document_id"""
        payload = {
            "content": "This is valid document content."
        }
        with self.assertRaises(ValidationError) as context:
            DocumentValidator.validate_payload(payload)
        # Check that the error was raised and contains info about missing field
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn("Missing required field: document_id", context.exception.errors[0])
    
    def test_missing_content(self):
        """Test validation with missing content"""
        payload = {
            "document_id": "DOC-123"
        }
        with self.assertRaises(ValidationError) as context:
            DocumentValidator.validate_payload(payload)
        self.assertEqual(len(context.exception.errors), 1)
        self.assertIn("Missing required field: content", context.exception.errors[0])
    
    def test_invalid_document_id_format(self):
        """Test validation with invalid document_id format"""
        invalid_ids = [
            "",  # Empty
            "DOC@123",  # Invalid character
            "DOC#123",  # Invalid character
            "A" * 101,  # Too long
            123,  # Not a string
        ]
        
        for doc_id in invalid_ids:
            payload = {
                "document_id": doc_id,
                "content": "Valid content here"
            }
            with self.assertRaises(ValidationError) as context:
                DocumentValidator.validate_payload(payload)
    
    def test_content_too_short(self):
        """Test validation with content too short"""
        payload = {
            "document_id": "DOC-123",
            "content": "Short"  # Less than 10 characters
        }
        with self.assertRaises(ValidationError) as context:
            DocumentValidator.validate_payload(payload)
        self.assertIn("Invalid content", context.exception.errors[0])
    
    def test_content_too_long(self):
        """Test validation with content exceeding max length"""
        payload = {
            "document_id": "DOC-123",
            "content": "A" * 1000001  # Exceeds 1MB limit
        }
        with self.assertRaises(ValidationError) as context:
            DocumentValidator.validate_payload(payload)
        self.assertIn("Invalid content", context.exception.errors[0])
    
    def test_sanitize_content(self):
        """Test content sanitization"""
        # Test null byte removal
        content = "Hello\x00World"
        sanitized = DocumentValidator.sanitize_content(content)
        self.assertEqual(sanitized, "HelloWorld")  # Null byte is removed, no space added
        
        # Test whitespace normalization
        content = "Hello    \t\t   World"
        sanitized = DocumentValidator.sanitize_content(content)
        self.assertEqual(sanitized, "Hello World")
        
        # Test control character removal
        content = "Hello\x01\x02World\x7F"
        sanitized = DocumentValidator.sanitize_content(content)
        self.assertEqual(sanitized, "HelloWorld")
        
        # Test that newlines are preserved (tabs are normalized to spaces)
        content = "Hello\nWorld\tTest"
        sanitized = DocumentValidator.sanitize_content(content)
        self.assertIn("\n", sanitized)
        self.assertIn("World Test", sanitized)  # Tab is normalized to space
    
    def test_valid_document_ids(self):
        """Test various valid document ID formats"""
        valid_ids = [
            "DOC-001",
            "DOC_001",
            "12345",
            "ABC123DEF456",
            "doc-with-multiple-dashes",
            "UPPER_CASE_ID",
            "lower_case_id"
        ]
        
        for doc_id in valid_ids:
            payload = {
                "document_id": doc_id,
                "content": "Valid content for testing"
            }
            # Should not raise exception
            DocumentValidator.validate_payload(payload)


if __name__ == "__main__":
    unittest.main()