from flask import Flask, request, jsonify
from analyzers.python_analyzer import analyze_python_code
from analyzers.javascript_analyzer import analyze_javascript_code

app = Flask(__name__)

@app.route('/basic', methods=['POST'])
def basic():
    """
    Basic route: returns a JSON with just the classification result.
    Returns 1 if AI-generated, 0 if human-written.
    """

    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"error": "No code provided."}), 400

    code = data['code']
    language = data.get('language', 'python').lower()

    if language == 'python':
        features, classification = analyze_python_code(code)
    elif language == 'javascript':
        features, classification = analyze_javascript_code(code)
    else:
        return jsonify({"error": f"Unsupported language: {language}"}), 400

    result = 1 if classification == "AI-Generated Code" else 0
    return jsonify({"result": result})

@app.route('/premium', methods=['POST'])
def premium():
    """
    Premium route: returns a JSON with the classification result and all extracted features.
    """

    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"error": "No code provided."}), 400

    code = data['code']
    language = data.get('language', 'python').lower()

    if language == 'python':
        features, classification = analyze_python_code(code)
    elif language == 'javascript':
        features, classification = analyze_javascript_code(code)
    else:
        return jsonify({"error": f"Unsupported language: {language}"}), 400

    result = 1 if classification == "AI-Generated Code" else 0

    response = {"result": result, "language": language}
    response.update(features)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
