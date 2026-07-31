from datasets import load_dataset
import pandas as pd
import os

# Create data folder if not exists
os.makedirs("data", exist_ok=True)

print("Loading MedQA dataset...")

# Load dataset
dataset = load_dataset("GBaker/MedQA-USMLE-4-options", split="train[:100]")

queries = []

for item in dataset:
    question = item["question"]
    queries.append(question)

# Create dataframe
df = pd.DataFrame({
    "query": queries,
    "label": ["SUFFICIENT"] * len(queries)
})

# Save CSV
df.to_csv("data/healthcare_queries.csv", index=False)

print(" Dataset created successfully.")
print("Saved at: data/healthcare_queries.csv")