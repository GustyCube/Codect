import ast
import tokenize
from io import BytesIO
import math

class PythonFeatureExtractor:
    """
    Extracts various features from Python source code to help differentiate AI-generated code from human-written code.
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
            print("Error tokenizing Python code:", e)

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
            print("Error parsing Python AST:", e)
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

def classify_python_code(features):
    """
    A heuristic-based classifier that uses extracted features to determine the likelihood of AI-generated Python code.
    Returns a score; if the score is high enough, we consider the code AI-generated.
    """
    score = 0

    if features["token_entropy"] < 3.5:
        score += 1

    if features["comment_ratio"] < 0.05 or features["comment_ratio"] > 0.2:
        score += 1

    if features["total_lines"] > 0 and (features["function_count"] / features["total_lines"]) > 0.1:
        score += 1

    if features["try_except_count"] == 0:
        score += 1

    if features["max_ast_depth"] < 5:
        score += 1

    if score >= 3:
        return "AI-Generated Code"
    return "Likely Human-Written Code"

def analyze_python_code(code):
    """
    Main function that extracts features from the Python code and returns both the feature dictionary and a classification.
    """
    extractor = PythonFeatureExtractor(code)
    features = extractor.extract_features()
    classification = classify_python_code(features)
    return features, classification
