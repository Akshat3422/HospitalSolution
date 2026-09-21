import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException
from nemoguardrails import RailsConfig, LLMRails
from src.pii_reduction.presidio_service import ClinicalPIIRedactor
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from typing import List

ROOT = Path(__file__).resolve().parents[2]   # src/api/main.py -> project root
load_dotenv(ROOT / ".env")

middleware = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⏳ Booting Enterprise AI Middlewares...")

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    # 1. Presidio (spaCy)
    middleware["redactor"] = ClinicalPIIRedactor()

    # 2. NeMo Guardrails
    config = RailsConfig.from_path(str(ROOT / "src" / "guardrils"))
    for model in config.models:
        if model.type == "main":
            model.parameters["api_key"] = groq_key
    middleware["rails"] = LLMRails(config)

    # 3. Local embedding model
    print("⏳ Loading local BioClinical ModernBERT embedding model...")
    middleware["embedder"] = SentenceTransformer(
        "NeuML/bioclinical-modernbert-base-embeddings"
    )

    print("✅ System Ready on port 8000.")

    yield

    middleware.clear()
    print("🛑 Middlewares shut down.")


app = FastAPI(lifespan=lifespan)

# --- DATABASE CONNECTION HELPER ---
def get_db_engine():
    try:  
        DATABASE_URL = os.getenv('DATABASE_URL')
    
        return create_engine(DATABASE_URL)
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {e}")


# --- MODELS ---
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    patient_id: str
    messages: List[ChatMessage]

class ClinicalQuery(BaseModel):
    patient_id: str
    prompt: str


# --- ENDPOINT 1: HEALTH CHECK (MOCK DB) ---
@app.post("/api/v1/clinical-query")
async def process_clinical_query(query: ClinicalQuery):
    try:
        raw_db_context = f"""
        Patient John Doe (ID: {query.patient_id}) was admitted on March 15th.
        Last recorded Furosemide dosage was 40mg IV. 
        Attending physician: Dr. Gregory House, ID: 20043.
        """

        redactor = middleware["redactor"]
        safe_context = redactor.redact_clinical_context(raw_text=raw_db_context)

        augmented_prompt = f"Clinical Context:\n{safe_context}\n\nUser Question: {query.prompt}"
        
        rails = middleware["rails"]
        response = await rails.generate_async(messages=[{"role": "user", "content": augmented_prompt}])

        return {
            "status": "success",
            "redacted_context_used": safe_context.strip(),
            "llm_response": response['content']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ENDPOINT 2: PRODUCTION CHAT (NATIVE PGVECTOR DB) ---
@app.post("/api/v1/chat")
async def process_chat(request: ChatRequest):
    try:
        latest_question = request.messages[-1].content
        print(latest_question)
        engine = get_db_engine()
        
        # 1. Embed the user's question into a 768-dim vector
        embedder = middleware["embedder"]
        query_vector = embedder.encode(latest_question).tolist()
        
        
        # 2. Native pgvector similarity search on patient_encounters table
        with engine.connect() as conn:
            print("patient_id received:", repr(request.patient_id), type(request.patient_id))
            print("DB:", conn.execute(text("SELECT current_database(), current_schema()")).fetchone())
            print("rows for patient:", conn.execute(
                text("SELECT count(*), count(clinical_embeddings) FROM patient_encounters WHERE subject_id = :s"),
                {"s": int(request.patient_id)}).fetchone())
            
            query = text("""
    WITH patient_rows AS MATERIALIZED (
        SELECT drug, dose_val_rx, dose_unit_rx, route, eventtype,
               test_name, comments, description, clinical_text,
               clinical_embeddings
        FROM patient_encounters
        WHERE subject_id = :subject_id AND clinical_embeddings IS NOT NULL
    )
    SELECT drug, dose_val_rx, dose_unit_rx, route, eventtype,
           test_name, comments, description, clinical_text
    FROM patient_rows
    ORDER BY clinical_embeddings <=> CAST(:query_embedding AS vector)
    LIMIT 30;
""")
            
            print("Executing query...")
            result = conn.execute(query, {
                "subject_id": int(request.patient_id),
                "query_embedding": str(query_vector)
            })
            rows = result.fetchall()
            
            if not rows:
                real_db_context = f"No historical records found for patient {request.patient_id}."
            else:
                context_lines = []
                for row in rows:
                    context_lines.append(
                        f"Drug: {row.drug} ({row.dose_val_rx} {row.dose_unit_rx}), Route: {row.route}, "
                        f"Event: {row.eventtype}, Test: {row.test_name}, Comments: {row.comments}, Diagnosis: {row.description}, Clinical Text: {row.clinical_text}"
                    )
                real_db_context = f"[Records for Patient ID: {request.patient_id}]\n" + "\n".join(context_lines)

        # 3. Redact the real context via Presidio
        redactor = middleware["redactor"]
        safe_context = redactor.redact_clinical_context(raw_text=real_db_context)
        
        # 4. Assemble Prompt
        augmented_prompt = f"Clinical Context:\n{safe_context}\n\nUser Question: {latest_question}"
        print(f"Augmented Prompt for Guardrails:\n{augmented_prompt}")
        
        # 5. Format History for Guardrails
        nemo_history = [{"role": msg.role, "content": msg.content} for msg in request.messages[:-1]]
        nemo_history.append({"role": "user", "content": augmented_prompt})
        
        # 6. Route through Guardrails
        rails = middleware["rails"]
        response = await rails.generate_async(messages=nemo_history)
        
        print(f"LLM Response:\n{response['content']}")
        return {"status": "success", "llm_response": response['content']}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ENDPOINT 3: FETCH UNIQUE PATIENTS (EMBEDDINGS ONLY) ---
@app.get("/api/v1/patients")
async def get_unique_patients():
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            # Only fetch patients who actually have generated embeddings
            query = text("""
                SELECT DISTINCT subject_id 
                FROM patient_encounters 
                WHERE subject_id IS NOT NULL AND clinical_embeddings IS NOT NULL 
                ORDER BY subject_id;
            """)
            result = conn.execute(query)
            patients = [str(row[0]) for row in result]
            
            return {"patients": patients if patients else ["No embedded patients found"]}
            
    except Exception as e:
        return {"patients": [], "error": str(e)}