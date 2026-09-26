# Zero-Trust Clinical EHR

A secure, intelligent Electronic Health Record (EHR) chat application designed with a zero-trust architecture. This project enables healthcare professionals to query patient historical records through an AI-powered conversational interface, prioritizing data privacy and safety using PII redaction and strict LLM guardrails.

## 🚀 Key Features

*   **Retrieval-Augmented Generation (RAG):** Uses native `pgvector` similarity search in PostgreSQL to retrieve relevant historical medical encounters based on the user's query.
*   **Zero-Trust Data Redaction:** Integrates **Microsoft Presidio** to detect and anonymize Personally Identifiable Information (PII) before context is sent to the LLM.
*   **LLM Guardrails:** Implements **NVIDIA NeMo Guardrails** to ensure the language model stays on-topic, provides clinically safe responses, and avoids harmful hallucinations.
*   **Domain-Specific Embeddings:** Utilizes the local `NeuML/bioclinical-modernbert-base-embeddings` model for highly accurate medical text vectorization.
*   **High-Performance Inference:** Powered by **Groq** for lightning-fast LLM responses.
*   **Intuitive UI:** A clean, easy-to-use interface built with **Streamlit**, with drop-down search for specific patient records.

## 🛠️ Technology Stack

*   **Backend:** Python, FastAPI
*   **Frontend:** Streamlit
*   **Database:** PostgreSQL with `pgvector` (Dockerized)
*   **AI/ML:** LangChain, SentenceTransformers, NVIDIA NeMo Guardrails, Presidio
*   **LLM Provider:** Groq
*   **Data Source:** MIMIC-IV Clinical Texts

## 📁 Project Structure

```text
hospital/
├── data/                       # Contains MIMIC-IV dataset and preprocessing scripts
├── src/
│   ├── api/                    # FastAPI backend (main.py)
│   ├── database/               # SQLAlchemy models and DB connection utilities
│   ├── embeddings/             # Scripts to generate and store vectors in pgvector
│   ├── guardrils/              # NeMo Guardrails configuration and custom rails
│   ├── pii_reduction/          # Microsoft Presidio setup for PII redaction
│   └── ui/                     # Streamlit frontend (app.py)
├── .env                        # Environment variables (needs to be created)
├── config.py                   # Global configuration loader
├── docker-compose.yml          # PostgreSQL + pgvector Docker setup
├── requirements.txt            # Python dependencies
└── Readme.md                   # Project documentation
```

## ⚙️ Setup and Installation

### 1. Prerequisites
*   Python 3.10+
*   Docker and Docker Compose
*   [Groq API Key](https://console.groq.com/keys)

### 2. Clone and Setup Environment
Navigate to the project directory and set up a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Ensure a `.env` file exists in the root of the project with the following keys:
```env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_postgres_db
DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@localhost:5433/your_postgres_db
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama3-70b-8192  # or your preferred Groq model
```

### 4. Start the Database
Spin up the PostgreSQL database equipped with `pgvector`:
```bash
docker-compose up -d
```

### 5. Data Ingestion & Embeddings
*Ensure your MIMIC dataset is in the `data/` folder.*
Run the embeddings scripts (in `src/embeddings/`) to process the clinical text, generate vectors using BioClinical ModernBERT, and store them in your local PostgreSQL database.

### 6. Run the Application Services
You will need two separate terminal windows for the backend and frontend.

**Start the FastAPI Backend:**
```bash
uvicorn src.api.main:app --reload --port 8000
```

**Start the Streamlit Frontend:**
```bash
streamlit run src/ui/app.py
```

Navigate to `http://localhost:8501` in your browser to interact with the EHR Chatbot.

## ⚠️ Disclaimer
**For Educational and Research Purposes Only.** 
This application generates AI summaries of medical records. It should **not** be used for actual diagnostic purposes, treatment planning, or in any real clinical setting. Always consult a qualified healthcare provider.
