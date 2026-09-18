import pandas as pd

from src.database.db import engine
from src.database.models import PatientEncounter


CSV_FILE = r"C:\Users\user\Desktop\hospital\data\mimic-iv-cleaned-medical-transcripts.csv"


df = pd.read_csv(CSV_FILE)

print("CSV loaded")
print(df.shape)
print(df.columns.tolist())


df.to_sql(
    PatientEncounter.__tablename__,
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000
)

print("Data inserted successfully!")