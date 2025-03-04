import math
import re
import json
from esprima import esprima  

class JavaScriptFeatureExtractor:
    """
    Extracts various features from JavaScript source code to help differentiate 
    AI-generated code from human-written code.
    """
    def __init__(self, code):
        self.code = code
        self.lines = code.splitlines()
        self.tokens = []
        self.token_counts = {}
        self.ast = None

    def tokenize_code(self):
        """Lexically tokenize the JavaScript code and count token frequencies."""
        try:
            tokens = esprima.tokenize(self.code)
            for token in tokens:
                token_str = token.value
                self.tokens.append(token_str)
                self.token_counts[token_str] = self.token_counts.get(token_str, 0) + 1
        except Exception as e:
            print("Error tokenizing JavaScript code:", e)

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
        """Counts the number of comment lines in the JavaScript code."""
        single_line_comments = re.findall(r'\/\/.*', self.code)
        multi_line_comments = re.findall(r'\/\*[\s\S]*?\*\/', self.code)
        
        return len(single_line_comments) + sum(c.count('\n') + 1 for c in multi_line_comments)

    def comment_ratio(self):
        """Calculates the ratio of comment lines to total lines."""
        total_lines = len(self.lines)
        if total_lines == 0:
            return 0
        return self.count_comments() / total_lines

    def parse_ast(self):
        """Parse the JavaScript code into an AST."""
        try:
            self.ast = esprima.parseScript(self.code, {'loc': True, 'range': True})
            return True
        except Exception as e:
            print("Error parsing JavaScript AST:", e)
            return False

    def ast_features(self):
        """
        Extracts various features from the JavaScript AST:
        - Function count (function declarations and expressions)
        - Loop count (for, while, do-while)
        - Try/catch block count
        - Maximum AST depth
        """
        if not self.parse_ast():
            return {
                "function_count": 0, 
                "loop_count": 0, 
                "try_catch_count": 0, 
                "max_depth": 0
            }

        features = {
            "function_count": 0,
            "loop_count": 0,
            "try_catch_count": 0,
            "max_depth": 0
        }

        def traverse_ast(node, depth=0):
            if not node:
                return
                
            features["max_depth"] = max(features["max_depth"], depth)
            
            if node.type in ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']:
                features["function_count"] += 1
                
            if node.type in ['ForStatement', 'ForInStatement', 'ForOfStatement', 'WhileStatement', 'DoWhileStatement']:
                features["loop_count"] += 1
                
            if node.type == 'TryStatement':
                features["try_catch_count"] += 1
                
            for key in node:
                if isinstance(node[key], dict) and 'type' in node[key]:
                    traverse_ast(node[key], depth + 1)
                elif isinstance(node[key], list):
                    for item in node[key]:
                        if isinstance(item, dict) and 'type' in item:
                            traverse_ast(item, depth + 1)

        ast_dict = json.loads(json.dumps(self.ast, default=lambda obj: obj.__dict__))
        traverse_ast(ast_dict)
        
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
            "try_catch_count": ast_feats["try_catch_count"],
            "max_ast_depth": ast_feats["max_depth"],
            "total_lines": len(self.lines)
        }
        return features

def classify_javascript_code(features):
    """
    A heuristic-based classifier that uses extracted features to determine the likelihood of AI-generated JavaScript code.
    Returns a score; if the score is high enough, we consider the code AI-generated.
    """
    score = 0

    if features["token_entropy"] < 3.8:  
        score += 1

    if features["comment_ratio"] < 0.03 or features["comment_ratio"] > 0.25:
        score += 1

    if features["total_lines"] > 0 and (features["function_count"] / features["total_lines"]) > 0.15:
        score += 1

    if features["try_catch_count"] == 0:
        score += 1

    if features["max_ast_depth"] < 4:
        score += 1

    if score >= 3:
        return "AI-Generated Code"
    return "Likely Human-Written Code"

def analyze_javascript_code(code):
    """
    Main function that extracts features from the JavaScript code and returns both the feature dictionary and a classification.
    """
    extractor = JavaScriptFeatureExtractor(code)
    features = extractor.extract_features()
    classification = classify_javascript_code(features)
    return features, classification