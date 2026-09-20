from sqlalchemy import create_engine, text
import pandas as pd
from config import DB_STRING

engine = create_engine(
    DB_STRING,
    echo=False
)

query = text("""
    UPDATE patient_encounters
    SET clinical_text = concat_ws(
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
    );
""")

with engine.begin() as conn:
    conn.execute(query)

print("clinical_text updated successfully.")

query_text=text("""
SELECT id,clinical_text
FROM patient_encounters
WHERE clinical_text IS NOT NULL""")

df=pd.read_sql(query_text, engine)

df.to_csv("clinical_texts.csv", index=False)