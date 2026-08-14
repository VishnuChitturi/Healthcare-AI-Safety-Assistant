from flask import Flask, request, jsonify
from flask_cors import CORS

from modules.decision_engine import process_query
from modules.response_generator import generate_response
from modules.retrieval_layer import ingest_guidelines

# Ingest and bootstrap vector RAG database if empty
ingest_guidelines()

app = Flask(__name__)
CORS(app)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Request body must be valid JSON with Content-Type: application/json."}), 400

        user_query = data.get("query")
        history = data.get("history", [])

        # Validate that query is present and is a string
        if user_query is None or not isinstance(user_query, str):
            return jsonify({"error": "Field 'query' is required and must be a non-null string."}), 400

        if history:
            query_or_history = history + [user_query]
        else:
            query_or_history = user_query

        decision = process_query(query_or_history)
        response = generate_response(user_query, decision)

        return jsonify({
            "decision": decision,
            "response": response
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)