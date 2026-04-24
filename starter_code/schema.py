from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime

# ==========================================
# ROLE 1: LEAD DATA ARCHITECT
# ==========================================
# Your task is to define the Unified Schema for all sources.
# This is v1. Note: A breaking change is coming at 11:00 AM!


# ==========================================
# SOURCE-SPECIFIC METADATA CLASSES
# ==========================================
# Use these classes with source_metadata field based on source_type.
# Example:
#   doc = UnifiedDocument(
#       document_id="lecture_01",
#       content="...",
#       source_type="PDF",
#       source_metadata=PDFMetadata(title="Introduction to ML", summary="...")
#   )


class PDFMetadata(BaseModel):
    """Metadata for PDF documents."""
    title: Optional[str] = None
    summary: Optional[str] = None


class HTMLMetadata(BaseModel):
    """Metadata for HTML documents."""
    url: Optional[str] = None
    node_count: Optional[int] = None


class CSVMetadata(BaseModel):
    """Metadata for CSV records."""
    record_count: Optional[int] = None
    columns: Optional[List[str]] = None


class TranscriptMetadata(BaseModel):
    """Metadata for transcript files."""
    speakers: Optional[List[str]] = None
    duration: Optional[str] = None


class CodeMetadata(BaseModel):
    """Metadata for source code files."""
    function_names: Optional[List[str]] = None
    class_names: Optional[List[str]] = None


# ==========================================
# UNIFIED DOCUMENT MODEL
# ==========================================
#
# Usage:
#   from starter_code.schema import UnifiedDocument, PDFMetadata
#
#   doc = UnifiedDocument(
#       document_id="unique_id",
#       content="Extracted text content...",
#       source_type="PDF",  # Must be: PDF, HTML, CSV, Transcript, or Code
#       author="John Doe",
#       timestamp=datetime.now(),
#       source_metadata=PDFMetadata(title="...", summary="...")
#   )
#
# Notes:
#   - source_type determines which metadata class to use
#   - source_metadata accepts: PDFMetadata, HTMLMetadata, CSVMetadata,
#     TranscriptMetadata, or CodeMetadata
#   - All metadata fields are Optional


class UnifiedDocument(BaseModel):
    # Core fields
    document_id: str  # Unique identifier for the document
    content: str  # Extracted/cleaned text content
    source_type: str  # Must be: 'PDF', 'HTML', 'CSV', 'Transcript', or 'Code'
    author: Optional[str] = "Unknown"
    timestamp: Optional[datetime] = None

    # Source-specific metadata (discriminated by source_type)
    # IMPORTANT: Pass the appropriate metadata class instance:
    #   - PDF source -> PDFMetadata(...)
    #   - HTML source -> HTMLMetadata(...)
    #   - CSV source -> CSVMetadata(...)
    #   - Transcript source -> TranscriptMetadata(...)
    #   - Code source -> CodeMetadata(...)
    source_metadata: Optional[
        Union[
            PDFMetadata,
            HTMLMetadata,
            CSVMetadata,
            TranscriptMetadata,
            CodeMetadata,
        ]
    ] = None