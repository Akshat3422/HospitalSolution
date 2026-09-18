import kagglehub
from kagglehub import KaggleDatasetAdapter

# Set the path to the file you'd like to load
file_path = "MIMIC_IV_Trasncript.csv"

# Load the latest version
df = kagglehub.load_dataset(
  KaggleDatasetAdapter.PANDAS,
  "isaacritharson/mimic-iv-cleaned-medical-transcripts",
  file_path,
)

print("First 5 records:", df.head())
df.to_csv("mimic-iv-cleaned-medical-transcripts.csv", index=False)