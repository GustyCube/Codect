import ast
import tokenize
from io import BytesIO
import math
from flask import Flask, request, jsonify

class CodeFeatureExtractor:
    """
    Extracts various features from source code to help differentiate AI-generated code from human-written code.
    """
    def __init__(self, code):
        self.code = code
        self.lines = code.splitlines()
        self.tokens = []
        self.token_counts = {}

    def tokenize_code(self):
        """Lexically tokenize the code and count token frequencies."""
        try:
            token_generator = tokenize.tokenize(BytesIO(self.code.encode('utf-8')).readline)
            for tok in token_generator:
                if tok.type in (tokenize.ENCODING, tokenize.ENDMARKER):
                    continue
                token_str = tok.string
                self.tokens.append(token_str)
                self.token_counts[token_str] = self.token_counts.get(token_str, 0) + 1
        except Exception as e:
            print("Error tokenizing code:", e)

    def calculate_token_entropy(self):
        """
        Calculates the entropy of the token distribution.
        Lower entropy may indicate overly consistent (potentially AI-generated) code.
        """
        total = len(self.tokens)
        if total == 0:
            return 0
        entropy = 0
        for token, count in self.token_counts.items():
            p = count / total
            entropy -= p * math.log(p, 2)
        return entropy

    def count_comments(self):
        """Counts the number of comment lines in the code."""
        comment_lines = [line for line in self.lines if line.strip().startswith("#")]
        return len(comment_lines)

    def comment_ratio(self):
        """Calculates the ratio of comment lines to total lines."""
        total_lines = len(self.lines)
        if total_lines == 0:
            return 0
        return self.count_comments() / total_lines

    def ast_features(self):
        """
        Parses the code into an AST and extracts features such as:
          - Function count
          - Loop count (for and while)
          - Try/except block count
          - Maximum depth of the AST (as a proxy for complexity)
        """
        try:
            tree = ast.parse(self.code)
        except Exception as e:
            print("Error parsing AST:", e)
            return {"function_count": 0, "loop_count": 0, "try_except_count": 0, "max_depth": 0}
        features = {"function_count": 0, "loop_count": 0, "try_except_count": 0, "max_depth": 0}

        def visit(node, depth=0):
            features["max_depth"] = max(features["max_depth"], depth)
            if isinstance(node, ast.FunctionDef):
                features["function_count"] += 1
            if isinstance(node, (ast.For, ast.While)):
                features["loop_count"] += 1
            if isinstance(node, ast.Try):
                features["try_except_count"] += 1
            for child in ast.iter_child_nodes(node):
                visit(child, depth + 1)

        visit(tree)
        return features

    def extract_features(self):
        """
        Runs all feature extraction methods and returns a dictionary with all metrics.
        """
        self.tokenize_code()
        token_entropy = self.calculate_token_entropy()
        comment_ratio = self.comment_ratio()
        ast_feats = self.ast_features()

        features = {
            "token_entropy": token_entropy,
            "comment_ratio": comment_ratio,
            "function_count": ast_feats["function_count"],
            "loop_count": ast_feats["loop_count"],
            "try_except_count": ast_feats["try_except_count"],
            "max_ast_depth": ast_feats["max_depth"],
            "total_lines": len(self.lines)
        }
        return features

def classify_code(features):
    """
    A heuristic-based classifier that uses extracted features to determine the likelihood of AI-generated code.
    Returns a score; if the score is high enough, we consider the code AI-generated.
    """
    score = 0

    # Lower token entropy could signal AI-generated code due to uniformity.
    if features["token_entropy"] < 3.5:
        score += 1

    # Comment ratio might be too low (sparse documentation) or too high (overly generic comments)
    if features["comment_ratio"] < 0.05 or features["comment_ratio"] > 0.2:
        score += 1

    # A high function count relative to total lines could indicate template-like code
    if features["total_lines"] > 0 and (features["function_count"] / features["total_lines"]) > 0.1:
        score += 1

    # Human-written code might include error handling. Zero try/except blocks could be suspicious.
    if features["try_except_count"] == 0:
        score += 1

    # A low maximum AST depth may imply very flat (and consistent) code structures
    if features["max_ast_depth"] < 5:
        score += 1

    # Based on the accumulated score, we set an arbitrary threshold.
    if score >= 3:
        return "AI-Generated Code"
    else:
        return "Likely Human-Written Code"

def analyze_code(code):
    """
    Main function that extracts features from the code and returns both the feature dictionary and a classification.
    """
    extractor = CodeFeatureExtractor(code)
    features = extractor.extract_features()
    classification = classify_code(features)
    return features, classification

# Create the Flask application
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
    features, classification = analyze_code(code)
    # Map the classification to integer output:
    # 1 for AI-Generated Code, 0 for Likely Human-Written Code.
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
    features, classification = analyze_code(code)
    result = 1 if classification == "AI-Generated Code" else 0

    # Include the result and all features in the response.
    response = {"result": result}
    response.update(features)
    return jsonify(response)

if __name__ == '__main__':
    # Run the Flask app. Adjust host and port as needed.
    app.run(debug=True)
