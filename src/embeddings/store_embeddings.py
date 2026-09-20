from sqlalchemy import create_engine, text
import pandas as pd

from config import DB_STRING


engine = create_engine(
    DB_STRING,
    echo=False
)


query = text("""
    SELECT
        id,

        concat_ws(
            ' | ',

            CASE
                WHEN admission_type IS NOT NULL
                THEN 'Admission: ' || admission_type
            END,

            CASE
                WHEN drug IS NOT NULL
                THEN 'Prescribed: ' || drug
            END,

            CASE
                WHEN test_name IS NOT NULL
                THEN 'Lab Test: ' || test_name
            END,

            CASE
                WHEN drg_severity IS NOT NULL
                THEN 'Severity Level: ' || drg_severity
            END,

            CASE
                WHEN description IS NOT NULL
                THEN 'Diagnosis: ' || description
            END,

            CASE
                WHEN comments IS NOT NULL
                THEN 'Notes: ' || LEFT(comments, 250)
            END

        ) AS clinical_text

    FROM patient_encounters

    WHERE clinical_embeddings IS NULL
""")


with engine.connect() as conn:

    df = pd.read_sql(
        query,
        conn
    )


df.to_csv(
    "clinical_texts.csv",
    index=False
)

print(f"Saved {len(df)} records.")