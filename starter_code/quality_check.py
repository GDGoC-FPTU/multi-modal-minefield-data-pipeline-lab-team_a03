# ==========================================
# ROLE 3: OBSERVABILITY & QA ENGINEER
# ==========================================
# Task: Implement quality gates to reject corrupt data or logic discrepancies.

def run_quality_gate(document_dict):
    # Handle both dict and Pydantic objects safely
    if hasattr(document_dict, 'model_dump'):
        doc_dict = document_dict.model_dump()
    elif isinstance(document_dict, dict):
        doc_dict = document_dict
    else:
        doc_dict = vars(document_dict) if hasattr(document_dict, '__dict__') else {}

    content = doc_dict.get('content', '')
    if not isinstance(content, str):
        content = str(content)

    # Reject documents with 'content' length < 20 characters
    if len(content) < 20:
        print(f"[QA FAIL] Document rejected: 'content' length ({len(content)}) is less than 20 characters.")
        return False
        
    # Reject documents containing toxic/error strings (e.g., 'Null pointer exception')
    toxic_strings = ['null pointer exception', 'traceback', 'internal server error']
    content_lower = content.lower()
    for toxic in toxic_strings:
        if toxic in content_lower:
            print(f"[QA FAIL] Document rejected: Found toxic string '{toxic}'.")
            return False
            
    # Flag discrepancies (e.g., if tax calculation comment says 8% but code says 10%)
    if '8%' in content and ('10%' in content or '0.10' in content):
        print(f"[QA FLAG] Discrepancy detected in document: Tax comment mentions 8% but code says 10%.")
        if isinstance(document_dict, dict):
            if 'source_metadata' not in document_dict:
                document_dict['source_metadata'] = {}
            document_dict['source_metadata']['has_discrepancy'] = True
        elif hasattr(document_dict, 'source_metadata'):
            document_dict.source_metadata['has_discrepancy'] = True
    
    return True
