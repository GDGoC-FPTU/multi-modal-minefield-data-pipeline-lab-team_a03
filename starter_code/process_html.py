from bs4 import BeautifulSoup
import os
import sys

# Thêm đường dẫn gốc vào sys.path để import được schema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from starter_code.schema import UnifiedDocument, HTMLMetadata

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract product data from the HTML table, ignoring boilerplate.

def parse_html_catalog(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    # ------------------------------------------
    
    documents = []
    
    # Use BeautifulSoup to find the table with id 'main-catalog'
    table = soup.find('table', id='main-catalog')
    if not table:
        return documents
        
    # Extract rows, handling 'N/A' or 'Liên hệ' in the price column.
    tbody = table.find('tbody')
    if not tbody:
        return documents
        
    rows = tbody.find_all('tr')
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 4:
            prod_id = cols[0].text.strip()
            name = cols[1].text.strip()
            category = cols[2].text.strip()
            price_text = cols[3].text.strip()
            
            # Xử lý giá tiền (bỏ qua nếu N/A hoặc Liên hệ)
            if price_text in ['N/A', 'Liên hệ']:
                price_val = None
            else:
                price_val = price_text
                
            content = f"Product: {name}, Category: {category}, Price: {price_val}"
            
            # Return a list of dictionaries for the UnifiedDocument schema.
            doc = UnifiedDocument(
                document_id=f"html_catalog_{prod_id}",
                content=content,
                source_type="HTML",
                author="System",
                source_metadata=HTMLMetadata(
                    url=file_path,
                    node_count=len(soup.find_all(True))
                )
            )
            documents.append(doc.model_dump(mode='json'))
            
    return documents
