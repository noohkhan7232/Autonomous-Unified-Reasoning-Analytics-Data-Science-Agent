import pandas as pd
import os

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"

COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num",
    "marital_status", "occupation", "relationship", "race", "sex",
    "capital_gain", "capital_loss", "hours_per_week", "native_country",
    "income"
]

df = pd.read_csv(
    URL,
    header=None,
    names=COLUMNS,
    skipinitialspace=True
)

output_path = os.path.join(DATA_DIR, "adult.csv")
df.to_csv(output_path, index=False)

print(f"Dataset saved to {output_path}")
