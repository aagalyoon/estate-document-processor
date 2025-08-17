#!/usr/bin/env python3
"""
Optional REST API for the Estate Document Processing System
Requires: pip install fastapi uvicorn
Run with: uvicorn api:app --reload
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import logging

try:
    from fastapi import FastAPI, HTTPException, status
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
except ImportError:
    print("FastAPI not installed. Run: pip install fastapi uvicorn")
    exit(1)

from agents import MasterAgent
from models.document import ProcessingResult
from utils.validators import DocumentValidator
from utils.exceptions import ValidationError, ProcessingError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Estate Document Processing API",
    description="API for processing estate-related documents with classification and compliance validation",
    version="1.0.0"
)

# Request/Response models
class DocumentRequest(BaseModel):
    document_id: str = Field(..., description="Unique identifier for the document")
    content: str = Field(..., description="Document content to process", min_length=10)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)
    service: str = "estate-document-processor"


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    document_id: Optional[str] = None


# Global agent instance (in production, consider using dependency injection)
master_agent = MasterAgent()


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Estate Document Processing API",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse()


@app.post("/process", 
         response_model=Dict[str, Any],
         responses={
             400: {"model": ErrorResponse, "description": "Invalid request"},
             500: {"model": ErrorResponse, "description": "Processing error"}
         })
async def process_document(request: DocumentRequest):
    """
    Process a document through the classification and compliance pipeline
    
    Returns:
        ProcessingResult with classification and compliance information
    """
    try:
        # Prepare payload
        payload = {
            "document_id": request.document_id,
            "content": request.content,
            "metadata": request.metadata
        }
        
        # Validate payload
        try:
            DocumentValidator.validate_payload(payload)
        except ValidationError as ve:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Validation failed",
                    "details": str(ve),
                    "document_id": request.document_id
                }
            )
        
        # Process document
        logger.info(f"Processing document via API: {request.document_id}")
        result = await master_agent.process(payload)
        
        # Convert to dict for JSON response
        return result.model_dump()
        
    except ValidationError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation failed",
                "details": str(ve),
                "document_id": request.document_id
            }
        )
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Processing failed",
                "details": str(e),
                "document_id": request.document_id
            }
        )


@app.get("/taxonomy", response_model=list)
async def get_taxonomy():
    """Get the document classification taxonomy"""
    from models.document import DocumentCategory
    
    return [
        {
            "name": category.display_name,
            "code": category.code
        }
        for category in DocumentCategory
    ]


@app.get("/agents/metrics", response_model=Dict[str, Any])
async def get_agent_metrics():
    """Get performance metrics from all agents"""
    return {
        "master_agent": master_agent.get_metrics(),
        "classification_agent": master_agent.classification_agent.get_metrics(),
        "compliance_agent": master_agent.compliance_agent.get_metrics()
    }


# Error handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation error",
            "details": str(exc),
            "document_id": exc.document_id
        }
    )


@app.exception_handler(ProcessingError)
async def processing_error_handler(request, exc: ProcessingError):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Processing error",
            "details": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)