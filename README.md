# Estate Document Processing System

An intelligent, agent-based system for automating triage and classification of estate-related documents with compliance validation.

## Overview

This system implements a multi-agent architecture designed to process documents related to estate settlement. It automatically classifies documents into categories and validates them against compliance rules specific to each document type.

## Architecture

The system consists of three specialized agents:

1. **Master Agent (Router)**: Orchestrates the document processing pipeline
2. **Classification Agent**: Analyzes content and assigns category codes based on estate-related taxonomy
3. **Compliance Agent**: Validates documents against category-specific rules

### Document Taxonomy

| Category | Code |
|----------|------|
| Death Certificate | 01.0000-50 |
| Will or Trust | 02.0300-50 |
| Property Deed | 03.0090-00 |
| Financial Statement | 04.5000-00 |
| Tax Document | 05.5000-70 |
| Miscellaneous | 00.0000-00 |

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/aagalyoon/estate-document-processor.git
cd estate-document-processor
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. (Optional) Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. (Optional) Install as a package:
```bash
pip install -e .
```

## Usage

### CLI Interface

The system provides a command-line interface for processing documents:

#### View available commands:
```bash
python cli.py --help
```

#### Process a document from file:
```bash
python cli.py process --document-id DOC-001 --file /path/to/document.txt
```

#### Process with inline content:
```bash
python cli.py process --document-id DOC-002 --content "Document content here..."
```

#### Run tests with mock documents:
```bash
python cli.py test
```

#### Test a specific document:
```bash
python cli.py test --test-name death_certificate_valid
```

#### List available mock documents:
```bash
python cli.py list-documents
```

#### Show document taxonomy:
```bash
python cli.py show-taxonomy
```

### Running Unit Tests

Execute the test suite:
```bash
python -m pytest tests/ -v
```

Or using unittest:
```bash
python tests/test_agents.py
python tests/test_validators.py
python tests/test_edge_cases.py
```

Run with coverage:
```bash
pytest tests/ --cov=agents --cov=models --cov=utils
```

## Project Structure

```
estate-document-processor/
├── agents/                      # Agent implementations
│   ├── base_agent.py           # Abstract base agent with metrics
│   ├── master_agent.py         # Routing/orchestration agent
│   ├── classification_agent.py # Document classification
│   └── compliance_agent.py     # Compliance validation
├── models/                      # Data models
│   └── document.py             # Document and result models
├── utils/                       # Utilities
│   ├── validators.py           # Input validation
│   └── exceptions.py           # Custom exceptions
├── data/                        # Test data
│   └── mock_documents.py       # Mock documents for testing
├── tests/                       # Unit tests
│   ├── test_agents.py          # Agent test cases
│   ├── test_validators.py      # Validator test cases
│   └── test_edge_cases.py      # Edge case testing
├── api.py                       # FastAPI REST endpoints (bonus)
├── cli.py                       # Command-line interface
├── setup.py                     # Package setup
├── requirements.txt             # Core dependencies
├── requirements-dev.txt         # Development dependencies
└── README.md                    # Documentation
```

## How It Works

### Processing Pipeline

1. **Document Receipt**: Master Agent receives document payload with ID and content
2. **Classification**: Document is analyzed for keywords and patterns to determine category
3. **Compliance Check**: Based on category, specific validation rules are applied
4. **Result Output**: Complete processing result with classification and compliance status

### Classification Logic

The Classification Agent uses keyword matching and pattern recognition to categorize documents:
- Analyzes document content for category-specific terms
- Calculates confidence scores based on keyword matches
- Returns category code and confidence level

### Compliance Rules

The Compliance Agent enforces category-specific validation:

**Death Certificate Requirements:**
- Must contain "Certificate of Death"
- Must have "Date of Death" field
- Must include deceased person's name
- Must have certificate number

**Will or Trust Requirements:**
- Must contain "Last Will and Testament" or "Trust Agreement"
- Must identify testator or grantor
- Must include beneficiary information

**Other Categories:**
- Property Deed: Must specify deed type and property description
- Financial Statement: Must contain account information and monetary amounts
- Tax Document: Must contain tax-related information and tax year
- Miscellaneous: Bypasses validation

## Key Design Decisions

### Agent Separation of Concerns
Each agent has a single responsibility, making the system modular and testable. This allows for easy extension and modification of individual components.

### Asynchronous Processing
Agents use async/await patterns to enable concurrent processing in future enhancements.

### Validation Strategy
Compliance rules are category-specific and configurable, allowing for easy updates to validation logic without modifying core agent code.

### Error Handling
The system gracefully handles errors at each stage, providing detailed error information while continuing to process when possible.

## Assumptions

1. Documents are provided as plain text (no OCR required)
2. Classification is based on keyword matching (suitable for prototype)
3. All documents are in English
4. Validation rules are static and predefined
5. No external services or databases are required

## Bonus Features Implemented

### REST API
The system includes a FastAPI-based REST API (`api.py`) with the following endpoints:
- `POST /process` - Process a document
- `GET /taxonomy` - Get classification taxonomy
- `GET /agents/metrics` - Get performance metrics
- `GET /health` - Health check endpoint

To run the API:
```bash
pip install fastapi uvicorn
uvicorn api:app --reload
```

### Performance Metrics
All agents track detailed performance metrics including:
- Processing counts and success rates
- Min/max/average processing times
- Error tracking and last processed timestamps

## Future Enhancements

- Integration with machine learning models for improved classification
- Support for PDF and image processing with OCR
- Database persistence for document tracking
- Real-time document streaming
- Multi-language support
- Dynamic rule configuration
- WebSocket support for real-time updates

## Testing

The system includes comprehensive test coverage:
- Unit tests for each agent
- Integration tests for the full pipeline
- Mock documents covering all categories
- Both valid and invalid document scenarios
