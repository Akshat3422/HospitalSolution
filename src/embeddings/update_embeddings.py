import ast
import pandas as pd
from sqlalchemy import create_engine, text
import joblib

from config import DB_STRING


engine = create_engine(DB_STRING)

query = text("""
    UPDATE patient_encounters
    SET clinical_embeddings = :embedding
    WHERE id = :patient_id
""")

CHUNK_SIZE = 5000

# Load pickle
dataset = joblib.load("dataset.pkl")

print(f"Total rows: {len(dataset):,}")

for start in range(0, len(dataset), CHUNK_SIZE):

    chunk = dataset.iloc[start:start + CHUNK_SIZE]

    records = []

    for _, row in chunk.iterrows():

        embedding = row["embedding"]

        # If embedding is stored as a string
        if isinstance(embedding, str):
            embedding = ast.literal_eval(embedding)

        patient_id = int(row["id"])

        records.append({
            "embedding": embedding,
            "patient_id": patient_id
        })

    # One transaction per chunk
    with engine.begin() as conn:
        conn.execute(query, records)

    print(
        f"Updated {min(start + CHUNK_SIZE, len(dataset)):,}"
        f"/{len(dataset):,}"
    )

print("All embeddings updated successfully.")