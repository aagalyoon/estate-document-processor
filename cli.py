#!/usr/bin/env python3

import asyncio
import click
import json
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.logging import RichHandler

from agents import MasterAgent
from data.mock_documents import MOCK_DOCUMENTS
from models.document import ProcessingResult

console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


def display_result(result: ProcessingResult):
    table = Table(title=f"Processing Result for Document {result.document_id}", show_header=True)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    
    table.add_row("Document ID", result.document_id)
    table.add_row("Status", f"[green]{result.status}[/green]" if result.status == "completed" else f"[red]{result.status}[/red]")
    table.add_row("Processed At", str(result.processed_at))
    
    table.add_section()
    table.add_row("Category", result.classification.category_name)
    table.add_row("Category Code", result.classification.category_code)
    table.add_row("Confidence", f"{result.classification.confidence:.2%}")
    
    table.add_section()
    table.add_row("Compliance", "[green]✓ Valid[/green]" if result.compliance.valid else "[red]✗ Invalid[/red]")
    if result.compliance.reason:
        table.add_row("Reason", result.compliance.reason)
    if result.compliance.checks_performed:
        table.add_row("Checks Performed", ", ".join(result.compliance.checks_performed))
    
    if result.errors:
        table.add_section()
        table.add_row("Errors", "[red]" + "\n".join(result.errors) + "[/red]")
    
    console.print(table)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def cli(verbose):
    setup_logging(verbose)


@cli.command()
@click.option('--document-id', '-d', required=True, help='Document ID to process')
@click.option('--file', '-f', type=click.Path(exists=True), help='Path to document file')
@click.option('--content', '-c', help='Document content (if not using file)')
@click.option('--output-json', is_flag=True, help='Output result as JSON')
def process(document_id: str, file: Optional[str], content: Optional[str], output_json: bool):
    if file:
        with open(file, 'r') as f:
            content = f.read()
    elif not content:
        console.print("[red]Error: Either --file or --content must be provided[/red]")
        return
    
    master_agent = MasterAgent()
    
    payload = {
        "document_id": document_id,
        "content": content,
        "metadata": {}
    }
    
    console.print(f"[cyan]Processing document {document_id}...[/cyan]")
    
    try:
        result = asyncio.run(master_agent.process(payload))
        
        if output_json:
            console.print(json.dumps(result.model_dump(), indent=2, default=str))
        else:
            display_result(result)
    
    except Exception as e:
        console.print(f"[red]Error processing document: {str(e)}[/red]")
        logger.exception("Processing failed")


@cli.command()
@click.option('--test-name', '-t', type=click.Choice(list(MOCK_DOCUMENTS.keys())), help='Specific test to run')
@click.option('--output-json', is_flag=True, help='Output results as JSON')
def test(test_name: Optional[str], output_json: bool):
    master_agent = MasterAgent()
    
    tests_to_run = [test_name] if test_name else list(MOCK_DOCUMENTS.keys())
    
    results = []
    summary_table = Table(title="Test Results Summary", show_header=True)
    summary_table.add_column("Document", style="cyan")
    summary_table.add_column("Expected Category", style="yellow")
    summary_table.add_column("Actual Category", style="white")
    summary_table.add_column("Classification", style="white")
    summary_table.add_column("Compliance", style="white")
    summary_table.add_column("Status", style="white")
    
    for doc_name in tests_to_run:
        doc_data = MOCK_DOCUMENTS[doc_name]
        console.print(f"\n[cyan]Testing: {doc_name}[/cyan]")
        
        try:
            result = asyncio.run(master_agent.process(doc_data))
            results.append(result)
            
            expected_category = doc_data["metadata"].get("expected_category", "Unknown")
            actual_category = result.classification.category_name
            classification_match = "✓" if expected_category == actual_category else "✗"
            
            should_fail = doc_data["metadata"].get("should_fail_compliance", False)
            compliance_correct = (not result.compliance.valid) if should_fail else result.compliance.valid
            compliance_status = "✓" if compliance_correct else "✗"
            
            status = "[green]PASS[/green]" if classification_match == "✓" and compliance_status == "✓" else "[red]FAIL[/red]"
            
            summary_table.add_row(
                doc_name,
                expected_category,
                actual_category,
                f"[green]{classification_match}[/green]" if classification_match == "✓" else f"[red]{classification_match}[/red]",
                f"[green]{compliance_status}[/green]" if compliance_status == "✓" else f"[red]{compliance_status}[/red]",
                status
            )
            
            if not output_json:
                display_result(result)
        
        except Exception as e:
            console.print(f"[red]Error testing {doc_name}: {str(e)}[/red]")
            summary_table.add_row(doc_name, "N/A", "N/A", "[red]✗[/red]", "[red]✗[/red]", "[red]ERROR[/red]")
    
    console.print("\n")
    console.print(summary_table)
    
    if output_json:
        output = [r.model_dump() for r in results]
        console.print(json.dumps(output, indent=2, default=str))


@cli.command()
def list_documents():
    table = Table(title="Available Mock Documents", show_header=True)
    table.add_column("Document Name", style="cyan")
    table.add_column("Document ID", style="yellow")
    table.add_column("Expected Category", style="green")
    table.add_column("Should Fail", style="red")
    
    for doc_name, doc_data in MOCK_DOCUMENTS.items():
        table.add_row(
            doc_name,
            doc_data["document_id"],
            doc_data["metadata"].get("expected_category", "Unknown"),
            "Yes" if doc_data["metadata"].get("should_fail_compliance", False) else "No"
        )
    
    console.print(table)


@cli.command()
def show_taxonomy():
    from models.document import DocumentCategory
    
    table = Table(title="Document Classification Taxonomy", show_header=True)
    table.add_column("Category", style="cyan")
    table.add_column("Code", style="yellow")
    
    for category in DocumentCategory:
        table.add_row(category.display_name, category.code)
    
    console.print(table)


def main():
    cli()


if __name__ == "__main__":
    main()