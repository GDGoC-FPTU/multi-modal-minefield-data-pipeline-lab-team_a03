import ast
import re
import os
import sys

# Thêm đường dẫn gốc vào sys.path để import được schema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from starter_code.schema import UnifiedDocument, CodeMetadata

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract docstrings and comments from legacy Python code.

def extract_logic_from_code(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    # ------------------------------------------
    
    # Use the 'ast' module to find docstrings for functions
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return {}
        
    docstrings = []
    function_names = []
    class_names = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_names.append(node.name)
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings.append(f"Function {node.name}: {docstring}")
        elif isinstance(node, ast.ClassDef):
            class_names.append(node.name)
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings.append(f"Class {node.name}: {docstring}")
        elif isinstance(node, ast.Module):
            docstring = ast.get_docstring(node)
            if docstring:
                docstrings.append(f"Module: {docstring}")
                
    # Use regex to find business rules in comments like "# Business Logic Rule 001"
    comments = re.findall(r'#.*', source_code)
    business_rules = [c for c in comments if "Business Logic Rule" in c]
    other_comments = [c for c in comments if "Business Logic Rule" not in c]
    
    content = "Docstrings:\n" + "\n".join(docstrings)
    content += "\n\nBusiness Rules:\n" + "\n".join(business_rules)
    content += "\n\nOther Comments:\n" + "\n".join(other_comments)
    
    # Return a dictionary for the UnifiedDocument schema.
    doc = UnifiedDocument(
        document_id="legacy_code_001",
        content=content,
        source_type="Code",
        author="System",
        source_metadata=CodeMetadata(
            function_names=function_names,
            class_names=class_names
        )
    )
    
    return doc.model_dump(mode='json')
