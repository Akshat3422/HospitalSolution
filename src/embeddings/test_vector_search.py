from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_STRING


# =========================
# DATABASE
# =========================

engine = create_engine(
    DB_STRING,
    echo=True
)

#=========================
# Adding CLinical Text Column
# #==========================
# clinical_text=pd.read_csv("clinical_texts.csv")

# query_text=text("""
# UPDATE patient_encounters
# SET clinical_text= :clinical_text
# WHERE id = :id
# """)
# with engine.begin() as conn:
#     for index, row in clinical_text.iterrows():
#         conn.execute(query_text, {"clinical_text": row["clinical_text"], "id": row["id"]})



# =========================
# MODEL
# =========================

model = SentenceTransformer(
    "NeuML/bioclinical-modernbert-base-embeddings"
)


# =========================
# QUERY
# =========================

query_text = (
    "patient with liver disease"
)


query_embedding = model.encode(
    query_text,
    convert_to_numpy=True,
    normalize_embeddings=True
)

# NumPy array -> Python list
query_embedding = query_embedding.tolist()


# =========================
# VECTOR SEARCH
# =========================

sql = text("""
    SELECT id, clinical_text, description, distance
FROM (
    SELECT DISTINCT ON (clinical_text)
        id,
        clinical_text,
        description,
        clinical_embeddings <=> CAST(:query_embedding AS vector) AS distance
    FROM patient_encounters
    WHERE clinical_embeddings IS NOT NULL
    ORDER BY
        clinical_text,
        clinical_embeddings <=> CAST(:query_embedding AS vector)
) AS unique_results
ORDER BY distance
LIMIT 10;
""")


with engine.connect() as conn:

    results = conn.execute(
        sql,
        {
            "query_embedding": str(query_embedding)
        }
    ).fetchall()


# =========================
# RESULTS
# =========================

for row in results:
    print(
        f"ID: {row.id}"
    )
    print(
        f"Text: {row.clinical_text}"
    )
    print(
        f"Distance: {row.distance}"
    )
    print("-" * 80)
    print(
        f"Description: {row.description}"
    )