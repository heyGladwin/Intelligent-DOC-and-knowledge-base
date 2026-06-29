from flask import Blueprint, request, jsonify
import os
import sys
from google import genai  # Use the new 2026 SDK
from pymongo import MongoClient

# 1. ROBUST PATH FIX: 
# This adds the PROJECT ROOT to the path so 'import ML' always works
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

try:
    from ML.utils import generate_embeddings 
except ImportError:
    # Fallback if you are running from inside the ML folder
    from utils import generate_embeddings

chat_bp = Blueprint('chat_bp', __name__)

# 2. 2026 CLIENT INITIALIZATION
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

# 3. MONGODB CONNECTION
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client['intelligentDoc']
collection = db['knowledge_base']

@chat_bp.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        user_query = data.get("question")

        # 4. VECTORIZE
        # generate_embeddings now returns 768-dim vectors
        embeddings = generate_embeddings([user_query])
        if not embeddings:
            return jsonify({"error": "Failed to generate embeddings"}), 500
        
        query_vector = embeddings[0]

        # 5. VECTOR SEARCH (Atlas)
        pipeline = [
            {"$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 10,
                "limit": 3
            }},
            {"$project": {"_id": 0, "content": 1}}
        ]
        
        docs = list(collection.aggregate(pipeline))
        context = "\n\n".join([d['content'] for d in docs])

        # 6. GENERATE ANSWER (Gemini 2.5 Flash)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"Context: {context}\n\nQuestion: {user_query}"
        )

        return jsonify({
            "answer": response.text,
            "sources": [d['content'] for d in docs]
        })

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500