class ProcessingError(Exception):
    """Base exception for document processing errors"""
    pass


class ValidationError(ProcessingError):
    """Raised when document validation fails"""
    def __init__(self, message: str, document_id: str = None, errors: list = None):
        super().__init__(message)
        self.document_id = document_id
        self.errors = errors or []


class ClassificationError(ProcessingError):
    """Raised when document classification fails"""
    def __init__(self, message: str, document_id: str = None):
        super().__init__(message)
        self.document_id = document_id


class ComplianceError(ProcessingError):
    """Raised when compliance validation fails"""
    def __init__(self, message: str, document_id: str = None, failed_checks: list = None):
        super().__init__(message)
        self.document_id = document_id
        self.failed_checks = failed_checks or []