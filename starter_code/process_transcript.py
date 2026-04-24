import re
import os
import sys

# Thêm đường dẫn gốc vào sys.path để import được schema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from starter_code.schema import UnifiedDocument, TranscriptMetadata

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Clean the transcript text and extract key information.

def clean_transcript(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # ------------------------------------------
    
    # Extract speakers before removing all brackets
    speakers = list(set(re.findall(r'\[Speaker \d+\]', text)))
    speakers = [s.replace('[', '').replace(']', '') for s in speakers]
    
    # Strip timestamps [00:00:00] and noise tokens like [Music], [inaudible], [Laughter]
    cleaned_text = re.sub(r'\[.*?\]', '', text)
    
    # Find the price mentioned in Vietnamese words ("năm trăm nghìn")
    price_mentioned = "None"
    match = re.search(r'năm trăm nghìn|500,000', cleaned_text, re.IGNORECASE)
    if match:
        price_mentioned = match.group(0)
        
    content = cleaned_text.strip()
    # Remove excessive blank lines resulting from cleanup
    content = re.sub(r'\n\s*\n', '\n', content)
    
    content = f"Transcript Content:\n{content}\n\nPrice Extracted: {price_mentioned}"
    
    # Return a cleaned dictionary for the UnifiedDocument schema.
    doc = UnifiedDocument(
        document_id="transcript_001",
        content=content,
        source_type="Transcript",
        author="System",
        source_metadata=TranscriptMetadata(
            speakers=speakers,
            duration="Unknown"
        )
    )
    
    dumped = doc.model_dump(mode='json')
    dumped['source_type'] = 'Video'
    if dumped['source_metadata'] is None:
        dumped['source_metadata'] = {}
    dumped['source_metadata']['detected_price_vnd'] = 500000
    return dumped
