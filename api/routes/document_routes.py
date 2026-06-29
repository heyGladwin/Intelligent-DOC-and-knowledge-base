from flask import Blueprint, request, jsonify
import os
import sys
from pymongo import MongoClient

# Link to your ML folder logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from ML.utils import extract_and_chunk_pdf, generate_embeddings 

document_bp = Blueprint('document_bp', __name__)

# MongoDB Setup
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client['intelligentDoc']
collection = db['knowledge_base']

@document_bp.route('/upload-knowledge', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        filename = file.filename
        
        # Save file temporarily to process it
        temp_path = f"temp_{filename}"
        file.save(temp_path)

        # 1. Use your ML utils to chunk the PDF
        chunks = extract_and_chunk_pdf(temp_path)
        
        # 2. Use your ML utils to generate vectors (768 dimensions)
        embeddings = generate_embeddings(chunks)

        # 3. Prepare and Insert into MongoDB
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "filename": filename,
                "content": chunk,
                "embedding": embeddings[i],
                "metadata": {"chunk_id": i}
            })

        if documents:
            collection.insert_many(documents)
        
        # Clean up the temp file
        os.remove(temp_path)

        return jsonify({
            "message": f"Successfully processed {len(documents)} chunks from {filename}",
            "status": "success"
        })

    except Exception as e:
        print(f"Upload Error: {e}")
        return jsonify({"error": str(e)}), 500