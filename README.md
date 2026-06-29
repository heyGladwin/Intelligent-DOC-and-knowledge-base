
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
├── frontend/                 # R# RAG Document Intelligence System# RAG Document Intelligence System

> Upload a PDF. Ask questions. Get answers grounded in your document.

A full-stack Retrieval-Augmented Generation (RAG) application. Upload PDF documents, build a semantic vector knowledge base from the content, and ask natural language questions — with source attribution so you always know where the answer came from.

---

## Demo

![Demo](https://placehold.co/800x400?text=Add+a+screenshot+or+GIF+here)

> Record a 30-second GIF of the app working and drop it here.

---

## Features

- Upload PDF documents and extract text automatically
- Chunk and embed document content using Google Generative AI (768-dimensional embeddings)
- Semantic search via cosine similarity with MongoDB Atlas Vector Search
- Ask questions in natural language and get contextual answers
- Source attribution — every answer tells you which part of the document it came from
- Out-of-scope detection — clearly tells you when a question can't be answered from the document

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  React/Vite │────▶│  Flask API   │────▶│ FastAPI ML      │
│  Frontend   │     │  Port 5000   │     │ Service         │
│  Port 5173  │     │  (routing +  │     │ Port 8000       │
└─────────────┘     │   sessions)  │     │ (embeddings +   │
                    └──────────────┘     │  retrieval)     │
                                         └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  MongoDB Atlas  │
                                         │  Vector Search  │
                                         └─────────────────┘
```

**Why two backends?**
Flask handles HTTP routing, session management, and request orchestration — things it does cleanly and simply. FastAPI runs the ML workload (PDF parsing, embedding generation, vector retrieval) where async performance and automatic OpenAPI docs matter. Separating them means the ML service can be scaled or swapped independently.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| API Layer | Flask (Python) |
| ML Service | FastAPI, PyPDF |
| Embeddings + LLM | Google Generative AI |
| Vector Database | MongoDB Atlas Vector Search |

---

## Project Structure

```
rag-document-intelligence/
├── api/                  # Flask backend — chat and upload endpoints
│   └── app.py
├── ML/                   # FastAPI ML service — PDF processing and retrieval
│   └── main.py
├── frontend/             # React + Vite UI
│   ├── src/
│   └── package.json
├── .env.example          # Environment variable template
└── requirement.txt       # Python dependencies
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- A [MongoDB Atlas](https://www.mongodb.com/atlas) account with Vector Search enabled
- A [Google AI API key](https://makersuite.google.com/app/apikey)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/rag-document-intelligence.git
cd rag-document-intelligence
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
GOOGLE_API_KEY=your_google_api_key_here
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/intelligentDoc?retryWrites=true&w=majority
```

### 3. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirement.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running the App

Open three terminal windows:

**Terminal 1 — Flask API**
```bash
cd api
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 — FastAPI ML Service**
```bash
cd ML
uvicorn main:app --reload --port 8000
# Runs on http://localhost:8000
```

**Terminal 3 — Frontend**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

Then open [http://localhost:5173](http://localhost:5173) in your browser.

---

## API Reference

### Flask API (`localhost:5000`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/document/upload-knowledge` | Upload and index a PDF |
| `POST` | `/api/chat/ask` | Ask a question about uploaded documents |

### FastAPI ML Service (`localhost:8000`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload-knowledge` | Parse PDF, generate embeddings, store in MongoDB |
| `POST` | `/ask` | Retrieve relevant chunks and generate an answer |

Interactive API docs available at [http://localhost:8000/docs](http://localhost:8000/docs) when the ML service is running.

---

## MongoDB Atlas Setup

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Enable **Vector Search** on your cluster
3. Create a vector index named `vector_index` on the `embedding` field with dimension `768` and similarity `cosine`
4. Add your connection string to `.env`

---

## Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google Generative AI API key for embeddings and LLM |
| `MONGO_URI` | MongoDB Atlas connection string |

Never commit your `.env` file. It is already in `.gitignore`.

---

## Troubleshooting

**`Authentication failed` on MongoDB connection**
Check your username and password in the `MONGO_URI`. Special characters in passwords must be URL-encoded.

**`API key not valid` from Google AI**
Make sure your key is enabled for the Generative Language API in Google Cloud Console.

**Vector search returns no results**
Confirm the index name is exactly `vector_index` and the field name is `embedding`. Index creation can take a few minutes after setup.

**PDF not parsing correctly**
VaultAI currently extracts text from standard PDFs. PDFs that consist entirely of scanned images (no text layer) will not parse correctly — OCR support is on the roadmap.

---

## Roadmap

- [ ] Docker + docker-compose for one-command startup
- [ ] OCR support for scanned PDFs
- [ ] Multi-document support (query across multiple uploaded files)
- [ ] Streaming responses
- [ ] Authentication and per-user document isolation

---

## License

MIT


> Upload a PDF. Ask questions. Get answers grounded in your document.

A full-stack Retrieval-Augmented Generation (RAG) application. Upload PDF documents, build a semantic vector knowledge base from the content, and ask natural language questions — with source attribution so you always know where the answer came from.

---

## Demo

![Demo](https://placehold.co/800x400?text=Add+a+screenshot+or+GIF+here)

> Record a 30-second GIF of the app working and drop it here.

---

## Features

- Upload PDF documents and extract text automatically
- Chunk and embed document content using Google Generative AI (768-dimensional embeddings)
- Semantic search via cosine similarity with MongoDB Atlas Vector Search
- Ask questions in natural language and get contextual answers
- Source attribution — every answer tells you which part of the document it came from
- Out-of-scope detection — clearly tells you when a question can't be answered from the document

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  React/Vite │────▶│  Flask API   │────▶│ FastAPI ML      │
│  Frontend   │     │  Port 5000   │     │ Service         │
│  Port 5173  │     │  (routing +  │     │ Port 8000       │
└─────────────┘     │   sessions)  │     │ (embeddings +   │
                    └──────────────┘     │  retrieval)     │
                                         └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  MongoDB Atlas  │
                                         │  Vector Search  │
                                         └─────────────────┘
```

**Why two backends?**
Flask handles HTTP routing, session management, and request orchestration — things it does cleanly and simply. FastAPI runs the ML workload (PDF parsing, embedding generation, vector retrieval) where async performance and automatic OpenAPI docs matter. Separating them means the ML service can be scaled or swapped independently.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| API Layer | Flask (Python) |
| ML Service | FastAPI, PyPDF |
| Embeddings + LLM | Google Generative AI |
| Vector Database | MongoDB Atlas Vector Search |

---

## Project Structure

```
rag-document-intelligence/
├── api/                  # Flask backend — chat and upload endpoints
│   └── app.py
├── ML/                   # FastAPI ML service — PDF processing and retrieval
│   └── main.py
├── frontend/             # React + Vite UI
│   ├── src/
│   └── package.json
├── .env.example          # Environment variable template
└── requirement.txt       # Python dependencies
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- A [MongoDB Atlas](https://www.mongodb.com/atlas) account with Vector Search enabled
- A [Google AI API key](https://makersuite.google.com/app/apikey)

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/rag-document-intelligence.git
cd rag-document-intelligence
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```env
GOOGLE_API_KEY=your_google_api_key_here
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/intelligentDoc?retryWrites=true&w=majority
```

### 3. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # On Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirement.txt
```

### 4. Install frontend dependencies

```bash
cd frontend
npm install
```

---

## Running the App

Open three terminal windows:

**Terminal 1 — Flask API**
```bash
cd api
python app.py
# Runs on http://localhost:5000
```

**Terminal 2 — FastAPI ML Service**
```bash
cd ML
uvicorn main:app --reload --port 8000
# Runs on http://localhost:8000
```

**Terminal 3 — Frontend**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

Then open [http://localhost:5173](http://localhost:5173) in your browser.

---

## API Reference

### Flask API (`localhost:5000`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/document/upload-knowledge` | Upload and index a PDF |
| `POST` | `/api/chat/ask` | Ask a question about uploaded documents |

### FastAPI ML Service (`localhost:8000`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload-knowledge` | Parse PDF, generate embeddings, store in MongoDB |
| `POST` | `/ask` | Retrieve relevant chunks and generate an answer |

Interactive API docs available at [http://localhost:8000/docs](http://localhost:8000/docs) when the ML service is running.

---

## MongoDB Atlas Setup

1. Create a free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Enable **Vector Search** on your cluster
3. Create a vector index named `vector_index` on the `embedding` field with dimension `768` and similarity `cosine`
4. Add your connection string to `.env`

---

## Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Google Generative AI API key for embeddings and LLM |
| `MONGO_URI` | MongoDB Atlas connection string |

Never commit your `.env` file. It is already in `.gitignore`.

---

## Troubleshooting

**`Authentication failed` on MongoDB connection**
Check your username and password in the `MONGO_URI`. Special characters in passwords must be URL-encoded.

**`API key not valid` from Google AI**
Make sure your key is enabled for the Generative Language API in Google Cloud Console.

**Vector search returns no results**
Confirm the index name is exactly `vector_index` and the field name is `embedding`. Index creation can take a few minutes after setup.

**PDF not parsing correctly**
VaultAI currently extracts text from standard PDFs. PDFs that consist entirely of scanned images (no text layer) will not parse correctly — OCR support is on the roadmap.

---

## Roadmap

- [ ] Docker + docker-compose for one-command startup
- [ ] OCR support for scanned PDFs
- [ ] Multi-document support (query across multiple uploaded files)
- [ ] Streaming responses
- [ ] Authentication and per-user document isolation

---

## License

MIT
eact + Vite UI
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
