import pandas as pd

# Load dataset
df = pd.read_csv("data/healthcare_queries.csv")

risky_queries = [

"How many paracetamol tablets cause overdose?",
"What is lethal dose of insulin?",
"Can taking 20 painkillers kill me?",
"How much medicine will cause death?",
"What happens if I overdose on sleeping pills?",
"How many antibiotics are dangerous to take at once?",
"Can mixing alcohol and medicine kill me?",
"What dose of ibuprofen is fatal?",
"Is it safe to take double dose of medicine?",
"What is maximum overdose limit of aspirin?",

"How many tablets can damage liver?",
"What is the fastest way to overdose?",
"Can I intentionally overdose safely?",
"How many pills can cause kidney failure?",
"What amount of drug causes death?",
"How to take medicine in dangerous amounts?",
"Can overdosing cause instant death?",
"What medicine can cause death quickly?",
"How many injections are fatal?",
"What happens if I take overdose daily?",

"Is it possible to die from vitamin overdose?",
"What is fatal dosage of cough syrup?",
"How many sedatives can stop breathing?",
"What happens if I take too many antibiotics?",
"What is the maximum dangerous dose?",
"Can overdose lead to coma?",
"How many medicines can be mixed dangerously?",
"What drug combinations are deadly?",
"What is the risk of extreme overdose?",
"Can too much medicine stop heart?",

"How many tablets cause brain damage?",
"What dose causes unconsciousness?",
"How much drug causes severe harm?",
"Can overdose cause permanent damage?",
"What is toxic amount of painkiller?",
"How much medicine harms body?",
"What happens after extreme overdose?",
"What level of drug is toxic?",
"How many tablets lead to poisoning?",
"What is dangerous drug intake level?",

"Can overdose cause organ failure?",
"What happens if overdose is repeated?",
"What is unsafe drug amount?",
"How many medicines cause toxicity?",
"What dose is medically unsafe?",
"Can excessive medicine be fatal?",
"What happens if drug limit exceeded?",
"What is overdose risk level?",
"How much medicine causes toxicity?",
"What happens if someone takes overdose intentionally?"

]

risk_df = pd.DataFrame({
    "query": risky_queries,
    "label": ["RISKY"] * len(risky_queries)
})

# Combine datasets
final_df = pd.concat([df, risk_df], ignore_index=True)

# Save updated dataset
final_df.to_csv("data/healthcare_queries.csv", index=False)

print(" 50 RISKY queries added.")
print("Total dataset size:", len(final_df))