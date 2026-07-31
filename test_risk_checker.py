from modules.risk_checker import check_risk

test_queries = [

"How many tablets cause overdose?",
"65-year-old male fever 3 days",
"Can too much medicine be fatal?",
"Person has headache",
"Severe chest pain and shortness of breath",
"I cannot breathe",
"Abdominal pain for 2 days",
"No fever or vomiting"

]

for q in test_queries:

    result = check_risk(q)

    print("Query:", q)
    print("Result:", result)
    print("-" * 40)