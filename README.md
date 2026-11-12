
# Nexus AI

Nexus AI is a document question-answering application with a Python backend, retrieval/ML utilities, and two available user interfaces:

- `frontend/`: React + Vite web interface
- `frontend.py`: Streamlit interface

## Project Structure

```text
api/       Flask API and route blueprints
ML/        Retrieval and machine-learning utilities
frontend/  React + Vite client
frontend.py
requirement.txt
```

## Requirements

- Python 3.10 or newer
- Node.js 18 or newer and npm
- A configured `.env` file for the model and database credentials used by the application

## Backend Setup

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirement.txt
```

Start the Flask API:

```powershell
python api/app.py
```

The API runs at `http://127.0.0.1:5000`.

## React Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, usually `http://localhost:5173`.

Useful commands:

```powershell
npm run build
npm run lint
npm run preview
```

## Streamlit Frontend

The older Streamlit client is started from the repository root:

```powershell
streamlit run frontend.py
```

The current Streamlit code sends requests to `http://127.0.0.1:8000`, while `api/app.py` starts Flask on port `5000`. Update the client or API port before using this interface end to end.

## API Health Check

Once the Flask API is running, visit or query:

```text
http://127.0.0.1:5000/
```

A healthy service returns a JSON response containing `status`, `version`, and `port`.

## Environment Variables

Keep secrets in `.env` and do not commit that file. Refer to the imports and service configuration in `api/`, `ML/`, and `frontend/src/services/` for the variables required by your local setup.
