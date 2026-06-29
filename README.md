# DocMind AI - PDF Knowledge Base Chat System

A full-stack RAG (Retrieval-Augmented Generation) application that lets users upload PDF documents, processes them into a searchable vector knowledge base, and enables AI-powered conversations grounded in those documents.

## 📋 What This Does

Users can:
- **Upload PDFs** - Add documents to the system (PDFs are extracted and chunked)
- **Vector Search** - Query documents using semantic similarity (not keyword search)
- **AI Chat** - Ask questions about uploaded documents and get answers from Google's Generative AI, grounded in the knowledge base
- **Track Sources** - See which documents were used to answer each question

## 🏗️ Project Structure

```
.
├── frontend/                 # React + Vite UI
│   ├── src/
│   │   ├── components/      # UI components (FileUpload, ChatMessage, etc.)
│   │   ├── pages/           # Main pages (Upload, Chatbot, Dashboard, etc.)
│   │   ├── services/        # API client (calls backend & ML services)
│   │   └── layouts/         # Layout components
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── api/                      # Flask backend API
│   ├── app.py               # API server
│   ├── routes/              # API endpoints
│   │   ├── chat_routes.py   # POST /api/chat/ask
│   │   └── document_routes.py
│   └── requirements.txt
│
└── ML/                       # FastAPI service for document processing
    ├── main.py              # PDF extraction, chunking, embedding, storage
    ├── utils.py             # PDF processing utilities
    ├── pipeline.txt         # Configuration
    └── requirements.txt
```

## 🚀 Tech Stack

### Frontend
- **React** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **JavaScript/JSX** - Frontend logic

### Backend API
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin request handling
- **PyMongo** - MongoDB client

### Document Processing & RAG
- **FastAPI** - Python async API framework
- **PyPDF/pdfplumber** - PDF extraction
- **Google Generative AI** - Embeddings and text generation
- **MongoDB Atlas** - Vector database (stores embeddings and documents)

### Infrastructure
- **MongoDB Atlas** - Cloud database with vector search capability
- **Google Cloud** - Generative AI API for embeddings and LLM

## 📦 Installation

### Prerequisites
- Node.js (v16+)
- Python (v3.9+)
- MongoDB Atlas account (free tier available)
- Google Cloud API key (for Generative AI)
- npm or yarn

### 1. Environment Setup

Create a `.env` file in the project root:
```env
# Google API
GOOGLE_API_KEY=your_google_api_key_here

# MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/intelligentDoc?retryWrites=true&w=majority
```

### 2. Backend API Setup

```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Document Processing Service Setup

```bash
cd ML
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Frontend Setup

```bash
cd frontend
npm install
```

## 🏃 Running the Application

### Terminal 1 - API Server
```bash
cd api
source venv/bin/activate
python app.py
```
Runs on `http://localhost:5000`

### Terminal 2 - Document Processing Service
```bash
cd ML
source venv/bin/activate
python main.py
```
Runs on `http://localhost:8000`

### Terminal 3 - Frontend
```bash
cd frontend
npm run dev
```
Runs on `http://localhost:5173`

## 📚 Features

### 📤 Document Upload
- Upload PDF files to the knowledge base
- Automatic PDF text extraction
- Document chunking for optimal context windows
- Metadata tracking (filename, timestamp)

### 🧠 Vector Embeddings
- Generate embeddings using Google Generative AI
- 768-dimensional embeddings for semantic similarity
- MongoDB vector search indexing
- Alignment verification between chunks and embeddings

### 💬 RAG Chat Interface
- Ask questions about uploaded documents
- Semantic search finds top 3 relevant document chunks
- Google Generative AI generates responses using retrieved context
- Source attribution (see which documents informed the answer)

### 📊 Dashboard
- View uploaded documents
- Quick stats overview
- Access to all features from central hub

### 🔍 Knowledge Base Search
- Query interface for document exploration
- Vector similarity-based retrieval
- Context-aware search results

## 🔧 API Endpoints

### Chat API (`/api/chat`)
- `POST /api/chat/ask` - Send a question
  - Request: `{"question": "What is...?"}`
  - Response: `{"answer": "...", "sources": [...]}`

### Document API (`/api/document`)
- Document upload and management endpoints

### ML Service (`http://localhost:8000`)
- `POST /upload-knowledge` - Upload PDF to knowledge base
- `POST /ask` - Query with vector search (used internally)

## 🗄️ Database

### MongoDB Atlas
- **Database**: `intelligentDoc`
- **Collection**: `knowledge_base`
- **Vector Index**: `vector_index` on `embedding` field
- **Fields**: `source` (filename), `content` (text chunk), `embedding` (768-dim vector)

### Vector Index Setup
```javascript
// Create vector search index in MongoDB Atlas:
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "similarity": "cosine",
      "dimensions": 768
    }
  ]
}
```

## 📝 Configuration

Key configuration files:
- `.env` - API keys and database connection
- `api/app.py` - Flask API configuration
- `ML/main.py` - Document processing pipeline configuration
- `frontend/vite.config.js` - Frontend build configuration

## 🧪 Testing

Test the API locally:

```bash
# Test chat endpoint
curl -X POST http://localhost:5000/api/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is in my documents?"}'

# Test PDF upload (from ML service)
curl -X POST http://localhost:8000/upload-knowledge \
  -F "file=@document.pdf"
```

## 📦 Dependencies

### API (`api/requirements.txt`)
- Flask - Web framework
- flask-cors - CORS handling
- pymongo - MongoDB client
- google-generativeai - Google embeddings API
- python-dotenv - Environment variables

### ML Service (`ML/requirements.txt`)
- fastapi - Async API framework
- fastapi-cors - CORS handling
- pymongo - MongoDB client
- google-generativeai - Embeddings generation
- PyPDF2 / pdfplumber - PDF extraction
- python-dotenv - Environment variables

### Frontend (`frontend/package.json`)
- React - UI framework
- Vite - Build tool
- Tailwind CSS - Styling

## 🔄 How It Works

```
User Upload Flow:
  Frontend (Upload Page) 
    ↓
  ML Service (FastAPI) - Extracts PDF text
    ↓
  Google Generative AI - Generates embeddings
    ↓
  MongoDB Atlas - Stores chunks + embeddings

User Query Flow:
  Frontend (Chat) - User asks question
    ↓
  API Server (Flask) - Receives question
    ↓
  Google Generative AI - Generates question embedding
    ↓
  MongoDB Atlas - Vector search (finds top 3 chunks)
    ↓
  Google Generative AI - Generates answer using retrieved context
    ↓
  API Response - Returns answer + sources to frontend
```

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/my-feature`)
2. Make your changes
3. Test thoroughly
4. Commit with clear messages
5. Push and open a pull request

## 📞 Support & Troubleshooting

### Common Issues

**Q: "MongoDB connection failed"**
- Verify `MONGO_URI` in `.env`
- Check MongoDB Atlas network access settings
- Ensure IP whitelist includes your machine

**Q: "Google API key invalid"**
- Verify `GOOGLE_API_KEY` in `.env`
- Check API is enabled in Google Cloud Console
- Ensure you have generative AI API enabled

**Q: "Vector search not working"**
- Confirm vector index is created in MongoDB
- Check embedding dimension matches (should be 768)
- Verify documents exist in knowledge base collection

For issues and questions, open an issue in the repository.

## 📄 License

[Add your license information here]

---

**Architecture**: RAG (Retrieval-Augmented Generation) system  
**Last Updated**: June 2026
