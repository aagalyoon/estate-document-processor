import re
from typing import Dict, Any, Optional
from utils.exceptions import ValidationError


class DocumentValidator:
    """Validates document payloads before processing"""
    
    MIN_CONTENT_LENGTH = 10
    MAX_CONTENT_LENGTH = 1000000  # 1MB text limit
    VALID_ID_PATTERN = re.compile(r'^[A-Za-z0-9\-_]+$')
    
    @classmethod
    def validate_payload(cls, payload: Dict[str, Any]) -> None:
        """
        Validates a document payload for required fields and constraints
        
        Args:
            payload: Document payload to validate
            
        Raises:
            ValidationError: If validation fails
        """
        errors = []
        
        # Check required fields
        if "document_id" not in payload:
            errors.append("Missing required field: document_id")
        elif not cls._validate_document_id(payload["document_id"]):
            errors.append(f"Invalid document_id format: {payload['document_id']}")
            
        if "content" not in payload:
            errors.append("Missing required field: content")
        elif not cls._validate_content(payload["content"]):
            errors.append("Invalid content: must be between 10 and 1000000 characters")
            
        if errors:
            raise ValidationError(
                "Document validation failed",
                document_id=payload.get("document_id"),
                errors=errors
            )
    
    @classmethod
    def _validate_document_id(cls, document_id: Any) -> bool:
        """Validates document ID format"""
        if not isinstance(document_id, str):
            return False
        if len(document_id) == 0 or len(document_id) > 100:
            return False
        return bool(cls.VALID_ID_PATTERN.match(document_id))
    
    @classmethod
    def _validate_content(cls, content: Any) -> bool:
        """Validates document content"""
        if not isinstance(content, str):
            return False
        content_length = len(content)
        return cls.MIN_CONTENT_LENGTH <= content_length <= cls.MAX_CONTENT_LENGTH
    
    @classmethod
    def sanitize_content(cls, content: str) -> str:
        """
        Sanitizes document content by removing potentially harmful characters
        
        Args:
            content: Raw document content
            
        Returns:
            Sanitized content
        """
        # Remove null bytes
        content = content.replace('\x00', '')
        
        # Remove control characters except newlines, tabs, and spaces
        sanitized = ''.join(char for char in content 
                           if char in '\n\t ' or 
                           (ord(char) >= 32 and ord(char) != 127))
        
        # Normalize excessive whitespace (but preserve newlines)
        lines = sanitized.split('\n')
        normalized_lines = []
        for line in lines:
            # Normalize spaces within each line
            normalized_line = ' '.join(line.split())
            normalized_lines.append(normalized_line)
        
        return '\n'.join(normalized_lines).strip()