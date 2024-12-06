from flask import Flask, request, jsonify
from src.generating_answers import QueryFAQ

# Initialize the Flask app
app = Flask(__name__)

# Initialize the QueryFAQ instance
query_faq = QueryFAQ()


@app.route('/query', methods=['POST'])
def get_answer():
    """
    Endpoint to get an answer based on the query.
    """
    try:
        # Get JSON data from the request
        data = request.get_json()
        if 'question' not in data:
            return jsonify({"error": "Missing 'question' field in request"}), 400

        # Process the query
        question = data['question']
        answer = query_faq.anwser_query(question)

        # Return the result
        return jsonify({"question": question, "answer": answer}), 200

    except Exception as e:
        # Handle any errors and return a 500 response
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
