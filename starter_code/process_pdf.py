import google.generativeai as genai
import os
import json
import sys
from dotenv import load_dotenv

# Thêm đường dẫn gốc vào sys.path để import được schema
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from starter_code.schema import UnifiedDocument, PDFMetadata

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def extract_pdf_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return None
        
    # Thay đổi model name để tránh lỗi 404 trên các phiên bản API cũ
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    import time
    max_retries = 4
    base_delay = 10
    
    # Upload with retry
    pdf_file = None
    for attempt in range(max_retries):
        try:
            print(f"Uploading {file_path} to Gemini... (Attempt {attempt + 1}/{max_retries})")
            pdf_file = genai.upload_file(path=file_path)
            break
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "quota" in err_msg or "exhausted" in err_msg:
                delay = base_delay * (2 ** attempt)
                print(f"Rate limit exceeded during upload. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to upload file to Gemini: {e}")
                return None
                
    if not pdf_file:
        print("Max retries exceeded for file upload.")
        return None
        
    prompt = """
Analyze this document and extract a summary and the author. 
Output exactly as a JSON object matching this exact format:
{
    "document_id": "pdf-doc-001",
    "content": "Summary: [Insert your 3-sentence summary here]",
    "source_type": "PDF",
    "author": "[Insert author name here]",
    "timestamp": null,
    "source_metadata": {
        "title": "[Insert Title here]",
        "summary": "[Insert your 3-sentence summary here]"
    }
}
"""
    
    # Generate content with retry
    response = None
    for attempt in range(max_retries):
        try:
            print(f"Generating content from PDF using Gemini... (Attempt {attempt + 1}/{max_retries})")
            response = model.generate_content([pdf_file, prompt])
            break
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "quota" in err_msg or "exhausted" in err_msg:
                delay = base_delay * (2 ** attempt)
                print(f"Rate limit exceeded during generation. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print(f"Failed to generate content: {e}")
                return None
                
    if not response:
        print("Max retries exceeded for content generation.")
        return None
        
    content_text = response.text
    
    # Simple cleanup if the response is wrapped in markdown json block
    if content_text.startswith("```json"):
        content_text = content_text[7:]
    if content_text.endswith("```"):
        content_text = content_text[:-3]
    if content_text.startswith("```"):
        content_text = content_text[3:]
        
    try:
        extracted_data = json.loads(content_text.strip())
        
        # Mapping to UnifiedDocument to validate schema
        meta = extracted_data.get('source_metadata', {})
        doc = UnifiedDocument(
            document_id=extracted_data.get('document_id', 'pdf-doc-001'),
            content=extracted_data.get('content', ''),
            source_type="PDF",
            author=extracted_data.get('author', 'Unknown'),
            timestamp=extracted_data.get('timestamp', None),
            source_metadata=PDFMetadata(
                title=meta.get('title', ''),
                summary=meta.get('summary', '')
            )
        )
        return doc.model_dump(mode='json')
        
    except Exception as e:
        print(f"Error parsing Gemini response or validating schema: {e}")
        return None
