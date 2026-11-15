# RAG Document Intelligence System

> Upload a PDF. Ask questions. Get answers grounded in your document.

A full-stack Retrieval-Augmented Generation (RAG) application. Upload PDF documents, build a semantic vector knowledge base from the content, and ask natural language questions — with source attribution so you always know where the answer came from.


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
