import os
import ssl
from pypdf import PdfReader
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_embeddings(text_list,task_type="RETRIEVAL_DOCUMENT"):
    """
    Converts text chunks into vectors.
    Model: gemini-embedding-001 (New 2026 Stable Standard)
    """
    if not text_list:
        return []
    
    all_embeddings = []
    batch_size = 50 # Smaller batches are safer in 2026
    
    try:
        for i in range(0, len(text_list), batch_size):
            batch = text_list[i : i + batch_size]
            
            # UPDATED MODEL NAME AND CONFIG
            result = client.models.embed_content(
                model="gemini-embedding-2", 
                contents=batch,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=3072 
                )
            )
            
            if result.embeddings:
                all_embeddings.extend([e.values for e in result.embeddings])
            
        return all_embeddings
    except Exception as e:
        print(f"❌ Embedding Error: {e}")
        return []

def extract_and_chunk_pdf(pdf_path, chunk_size=1000, chunk_overlap=200):
    """
    Cleanly extracts text and creates overlapping chunks to prevent context loss.
    """
    chunks = []
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        
        for page in reader.pages:
            content = page.extract_text()
            if content:
                # Clean null bytes that crash databases
                full_text += content.replace('\x00', '') + " "
        
        if not full_text.strip():
            return []

        # Create overlapping chunks
        for i in range(0, len(full_text), chunk_size - chunk_overlap):
            chunk = full_text[i : i + chunk_size].strip()
            if len(chunk) > 10: # Ignore tiny fragments
                chunks.append(chunk)
                
        return chunks
    except Exception as e:
        print(f"❌ PDF Processing Error: {e}")
        return []