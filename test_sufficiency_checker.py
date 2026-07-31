from modules.sufficiency_checker import check_sufficiency

test_queries = [

"Can I take medicine?",

"65-year-old male with fever for 3 days",

"Person has headache",

"70-year-old diabetic with chest pain for 2 hours"

]

for q in test_queries:

    result = check_sufficiency(q)

    print("Query:", q)
    print("Result:", result["status"])
    print("Details:", {
        "age_present": result["age_present"],
        "symptoms_present": result["symptoms_present"],
        "duration_present": result["duration_present"],
        "source": result["source"],
        "errors": result["errors"],
    })
    print("-" * 40)