import pandas as pd
import math
from datetime import datetime
import os
import sys

# Thêm đường dẫn gốc vào sys.path để import được schema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from starter_code.schema import UnifiedDocument, CSVMetadata

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Process sales records, handling type traps and duplicates.

def process_sales_csv(file_path):
    # --- FILE READING (Handled for students) ---
    df = pd.read_csv(file_path)
    # ------------------------------------------
    
    # Remove duplicate rows based on 'id'
    df = df.drop_duplicates(subset=['id'], keep='first')
    
    # Clean 'price' column
    def clean_price(val):
        if pd.isna(val) or val in ['N/A', 'NULL', 'Liên hệ']:
            return None
        val = str(val).strip().lower()
        if 'five dollars' in val:
            return 5.0
        val = val.replace('$', '').replace(',', '')
        try:
            return float(val)
        except ValueError:
            return None
            
    df['price_cleaned'] = df['price'].apply(clean_price)
    
    # Normalize 'date_of_sale' into a single format (YYYY-MM-DD)
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="pandas")
    df['date_of_sale_cleaned'] = pd.to_datetime(df['date_of_sale'], errors='coerce')
    df['date_of_sale_str'] = df['date_of_sale_cleaned'].dt.strftime('%Y-%m-%d')
    
    # Return a list of dictionaries for the UnifiedDocument schema.
    documents = []
    columns = df.columns.tolist()
    
    for _, row in df.iterrows():
        doc_id = f"csv-{row['id']}"
        content = f"Product: {row['product_name']}, Price: {row['price_cleaned']}, Date: {row['date_of_sale_str']}"
        
        author = row.get('seller_id', "Unknown")
        if pd.isna(author):
            author = "Unknown"
            
        timestamp = row['date_of_sale_cleaned']
        if pd.isna(timestamp):
            timestamp = None
            
        doc = UnifiedDocument(
            document_id=str(doc_id),
            content=content,
            source_type="CSV",
            author=str(author),
            timestamp=timestamp,
            source_metadata=CSVMetadata(
                record_count=1,
                columns=columns
            )
        )
        documents.append(doc.model_dump(mode='json'))
        
    return documents
