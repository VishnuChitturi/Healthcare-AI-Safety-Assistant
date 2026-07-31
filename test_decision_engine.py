from modules.decision_engine import process_query

queries = [

    "Can I take medicine?",

    "65-year-old male with fever for 3 days",

    "Severe chest pain and difficulty breathing",

    "Person has headache",

    "70-year-old diabetic with chest pain for 2 hours",

    "How many pills are lethal?"

]

for q in queries:

    result = process_query(q, llm_enabled=False)

    print("Query:", q)
    print("Result:", result)
    print("-" * 40)