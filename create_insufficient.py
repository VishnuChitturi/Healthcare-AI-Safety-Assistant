import pandas as pd

# Load existing dataset
df = pd.read_csv("data/healthcare_queries.csv")

insufficient_queries = []

print("Creating insufficient queries...")

for q in df["query"]:

    # Remove detailed info (simple shortening)
    short_q = q.split("?")[0]

    # Keep only first few words
    words = short_q.split()

    shortened = " ".join(words[:6])

    insufficient_queries.append(shortened)

# Create insufficient dataframe
ins_df = pd.DataFrame({
    "query": insufficient_queries,
    "label": ["INSUFFICIENT"] * len(insufficient_queries)
})

# Combine datasets
final_df = pd.concat([df, ins_df], ignore_index=True)

# Save updated dataset
final_df.to_csv("data/healthcare_queries.csv", index=False)

print("✅ 100 INSUFFICIENT queries added.")
print("Total dataset size:", len(final_df))