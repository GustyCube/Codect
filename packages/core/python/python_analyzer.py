import ast
import math
import re
from collections import Counter
from typing import Dict, List, Tuple, Union

class ImprovedPythonAnalyzer:
    """
    Enhanced analyzer that focuses on patterns that truly distinguish AI vs human code
    """

    def __init__(self, code: str):
        self.code = code
        self.lines = code.splitlines()
        self.tokens = []
        self.tree = None

    def extract_all_features(self) -> Dict[str, Union[bool, float, int, str]]:
        """Extract comprehensive features for classification"""
        features = {}

        # Parse AST
        try:
            self.tree = ast.parse(self.code)
        except:
            return self._get_default_features()

        # Extract different feature categories
        features.update(self._extract_structural_patterns())
        features.update(self._extract_naming_patterns())
        features.update(self._extract_consistency_metrics())
        features.update(self._extract_code_smell_indicators())
        features.update(self._extract_ai_specific_patterns())

        return features

    def _extract_structural_patterns(self) -> Dict[str, Union[bool, float]]:
        """Extract structural code patterns"""
        features = {
            'has_main_guard': False,
            'has_docstrings': False,
            'function_length_variance': 0.0,
            'nested_function_depth': 0,
            'uses_comprehensions': False,
            'uses_walrus_operator': False,
            'uses_f_strings': False,
            'import_organization_score': 0.0,
        }

        if not self.tree:
            return features

        # Check for if __name__ == "__main__"
        for node in ast.walk(self.tree):
            if isinstance(node, ast.If):
                if self._is_main_guard(node):
                    features['has_main_guard'] = True

        # Analyze functions
        functions = [node for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)]
        if functions:
            # Check for docstrings
            for func in functions:
                if ast.get_docstring(func):
                    features['has_docstrings'] = True
                    break

            # Function length variance (AI tends to be more uniform)
            func_lengths = [len(func.body) for func in functions]
            if len(func_lengths) > 1:
                features['function_length_variance'] = self._std_dev([float(x) for x in func_lengths])

        # Check for comprehensions
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                features['uses_comprehensions'] = True
                break

        # Check for walrus operator (3.8+)
        for node in ast.walk(self.tree):
            if isinstance(node, ast.NamedExpr):
                features['uses_walrus_operator'] = True
                break

        # Check for f-strings
        for node in ast.walk(self.tree):
            if isinstance(node, ast.JoinedStr):
                features['uses_f_strings'] = True
                break

        # Import organization (AI often groups perfectly)
        features['import_organization_score'] = self._analyze_import_organization()

        return features

    def _extract_naming_patterns(self) -> Dict[str, Union[bool, float]]:
        """Analyze variable and function naming patterns"""
        features = {
            'naming_consistency_score': 0.0,
            'uses_snake_case_ratio': 0.0,
            'meaningful_name_ratio': 0.0,
            'single_letter_var_ratio': 0.0,
            'avg_name_length': 0.0,
        }

        if not self.tree:
            return features

        # Collect all names
        names: List[str] = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name):
                names.append(node.id)
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                names.append(node.name)

        if not names:
            return features

        # Analyze naming patterns
        snake_case_count = sum(1 for name in names if self._is_snake_case(name))
        features['uses_snake_case_ratio'] = snake_case_count / len(names)

        # Single letter variables (excluding common ones like i, j, k in loops)
        single_letter = [n for n in names if len(n) == 1 and n not in 'ijkxyz']
        features['single_letter_var_ratio'] = len(single_letter) / len(names)

        # Average name length
        features['avg_name_length'] = sum(len(n) for n in names) / len(names)

        # Meaningful names (rough heuristic)
        common_meaningless = {'tmp', 'temp', 'var', 'val', 'res', 'ret', 'obj', 'item'}
        meaningful = [n for n in names if len(n) > 3 and n.lower() not in common_meaningless]
        features['meaningful_name_ratio'] = len(meaningful) / len(names)

        return features

    def _extract_consistency_metrics(self) -> Dict[str, float]:
        """Measure code consistency (AI tends to be very consistent)"""
        features = {
            'indentation_consistency': 0.0,
            'quote_consistency': 0.0,
            'spacing_consistency': 0.0,
            'pattern_repetition_score': 0.0,
        }

        # Indentation consistency
        indents: List[int] = []
        for line in self.lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indents.append(indent)

        if indents:
            # Check if all indents are multiples of 4 (or 2)
            base_indent = min(i for i in indents if i > 0) if any(i > 0 for i in indents) else 4
            consistent = all(i % base_indent == 0 for i in indents)
            features['indentation_consistency'] = 1.0 if consistent else 0.5

        # Quote consistency
        single_quotes = self.code.count("'")
        double_quotes = self.code.count('"')
        total_quotes = single_quotes + double_quotes
        if total_quotes > 0:
            features['quote_consistency'] = max(single_quotes, double_quotes) / total_quotes

        # Pattern repetition (AI often repeats similar structures)
        features['pattern_repetition_score'] = self._calculate_pattern_repetition()

        return features

    def _extract_code_smell_indicators(self) -> Dict[str, bool]:
        """Detect code smells and anti-patterns more common in human code"""
        features = {
            'has_todo_comments': False,
            'has_debug_prints': False,
            'has_commented_code': False,
            'has_magic_numbers': False,
            'has_long_lines': False,
            'has_trailing_whitespace': False,
            'inconsistent_returns': False,
        }

        # TODO/FIXME comments (humans leave these, AI rarely does)
        todo_pattern = re.compile(r'#\s*(TODO|FIXME|HACK|XXX|BUG|REFACTOR)', re.IGNORECASE)
        features['has_todo_comments'] = bool(todo_pattern.search(self.code))

        # Debug prints
        debug_pattern = re.compile(r'print\s*\(["\']debug|console\.log|debugger')
        features['has_debug_prints'] = bool(debug_pattern.search(self.code))

        # Commented out code (rough heuristic)
        commented_code_pattern = re.compile(r'#\s*(if|for|while|def|class|import|return)\s')
        features['has_commented_code'] = bool(commented_code_pattern.search(self.code))

        # Magic numbers (numbers that aren't 0, 1, 2)
        if self.tree:
            for node in ast.walk(self.tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    if node.value not in (0, 1, 2, -1, 10, 100, 1000):
                        features['has_magic_numbers'] = True
                        break

        # Long lines
        features['has_long_lines'] = any(len(line) > 100 for line in self.lines)

        # Trailing whitespace
        features['has_trailing_whitespace'] = any(line.rstrip() != line for line in self.lines)

        return features

    def _extract_ai_specific_patterns(self) -> Dict[str, float]:
        """Extract patterns specific to AI-generated code"""
        features = {
            'perfect_pep8_score': 0.0,
            'generic_example_score': 0.0,
            'over_explanation_score': 0.0,
            'placeholder_score': 0.0,
            'uniform_complexity': 0.0,
        }

        # Generic examples (AI loves foo, bar, example, test)
        generic_pattern = re.compile(r'\b(foo|bar|baz|example|test|sample|demo)\b', re.IGNORECASE)
        generic_matches = len(generic_pattern.findall(self.code))
        features['generic_example_score'] = min(generic_matches / max(len(self.lines), 1), 1.0)

        # Over-explanation in comments
        if self.lines:
            comment_lines = [l for l in self.lines if l.strip().startswith('#')]
            avg_comment_length = sum(len(c) for c in comment_lines) / max(len(comment_lines), 1)
            features['over_explanation_score'] = min(avg_comment_length / 80, 1.0)

        # Placeholder patterns
        placeholder_pattern = re.compile(r'(Your|TODO:|FIXME:|INSERT|REPLACE|your_|my_|some_)', re.IGNORECASE)
        features['placeholder_score'] = min(len(placeholder_pattern.findall(self.code)) / 10, 1.0)

        return features

    def _is_main_guard(self, node: ast.If) -> bool:
        """Check if node is if __name__ == "__main__" """
        if not isinstance(node.test, ast.Compare):
            return False
        if not isinstance(node.test.left, ast.Name) or node.test.left.id != "__name__":
            return False
        if not any(isinstance(op, ast.Eq) for op in node.test.ops):
            return False
        if not any(isinstance(comp, ast.Constant) and comp.value == "__main__" 
                  for comp in node.test.comparators):
            return False
        return True

    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention"""
        return bool(re.match(r'^[a-z_][a-z0-9_]*$', name))

    def _analyze_import_organization(self) -> float:
        """Score how well imports are organized (AI tends to organize perfectly)"""
        import_lines: List[Tuple[int, str]] = []
        for i, line in enumerate(self.lines):
            if line.strip().startswith(('import ', 'from ')):
                import_lines.append((i, line.strip()))

        if len(import_lines) < 2:
            return 0.0

        # Check if imports are grouped and sorted
        groups = []
        current_group = [import_lines[0]]

        for i in range(1, len(import_lines)):
            if import_lines[i][0] - import_lines[i-1][0] == 1:
                current_group.append(import_lines[i])
            else:
                groups.append(current_group)
                current_group = [import_lines[i]]
        groups.append(current_group)

        # Check if each group is sorted
        sorted_score = 0
        for group in groups:
            lines = [line for _, line in group]
            if lines == sorted(lines):
                sorted_score += 1

        return sorted_score / len(groups)

    def _calculate_pattern_repetition(self) -> float:
        """Calculate how repetitive the code structure is"""
        if not self.tree:
            return 0.0

        # Extract statement patterns
        patterns: List[str] = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.stmt):
                pattern = type(node).__name__
                patterns.append(pattern)

        if len(patterns) < 5:
            return 0.0

        # Look for repeated sequences
        pattern_counts = Counter()
        for i in range(len(patterns) - 2):
            trigram = tuple(patterns[i:i+3])
            pattern_counts[trigram] += 1

        # High repetition score if same patterns appear frequently
        max_count = max(pattern_counts.values()) if pattern_counts else 0
        return min(max_count / len(patterns), 1.0)

    def _std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation without numpy"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def _get_default_features(self) -> Dict[str, Union[bool, float, int]]:
        """Return default features when parsing fails"""
        return {
            'has_main_guard': False,
            'has_docstrings': False,
            'function_length_variance': 0.0,
            'nested_function_depth': 0,
            'uses_comprehensions': False,
            'uses_walrus_operator': False,
            'uses_f_strings': False,
            'import_organization_score': 0.0,
            'naming_consistency_score': 0.0,
            'uses_snake_case_ratio': 0.0,
            'meaningful_name_ratio': 0.0,
            'single_letter_var_ratio': 0.0,
            'avg_name_length': 0.0,
            'indentation_consistency': 0.0,
            'quote_consistency': 0.0,
            'spacing_consistency': 0.0,
            'pattern_repetition_score': 0.0,
            'has_todo_comments': False,
            'has_debug_prints': False,
            'has_commented_code': False,
            'has_magic_numbers': False,
            'has_long_lines': False,
            'has_trailing_whitespace': False,
            'inconsistent_returns': False,
            'perfect_pep8_score': 0.0,
            'generic_example_score': 0.0,
            'over_explanation_score': 0.0,
            'placeholder_score': 0.0,
            'uniform_complexity': 0.0,
        }


class ImprovedClassifier:
    """
    Weighted classification system that considers feature importance
    """

    def __init__(self):
        # Feature weights based on importance
        self.weights = {
            # Strong AI indicators (positive weight = more likely AI)
            'import_organization_score': 2.5,
            'indentation_consistency': 2.0,
            'quote_consistency': 1.5,
            'pattern_repetition_score': 3.0,
            'generic_example_score': 3.5,
            'perfect_pep8_score': 2.0,
            'uniform_complexity': 2.5,

            # Strong human indicators (negative weight = more likely human)
            'has_todo_comments': -3.0,
            'has_debug_prints': -2.5,
            'has_commented_code': -2.0,
            'has_magic_numbers': -1.5,
            'has_long_lines': -1.0,
            'has_trailing_whitespace': -2.0,
            'single_letter_var_ratio': -1.0,
            'function_length_variance': -1.5,  # Humans have more variance

            # Neutral/context-dependent
            'has_main_guard': -0.5,  # Slightly human
            'has_docstrings': 0.5,   # Could go either way
            'uses_comprehensions': -0.5,  # Slightly human (elegant code)
            'uses_f_strings': 0.0,   # Neutral
            'meaningful_name_ratio': -0.3,  # Good names slightly human
        }

    def classify(self, features: Dict[str, Union[bool, float, int, str]]) -> Tuple[str, float]:
        """
        Classify code and return result with confidence score
        """
        score = 0.0

        # Calculate weighted score
        for feature, value in features.items():
            if feature in self.weights:
                # Convert boolean to float, skip strings
                if isinstance(value, bool):
                    numeric_value = 1.0 if value else 0.0
                elif isinstance(value, (int, float)):
                    numeric_value = float(value)
                else:
                    # Skip non-numeric values like strings
                    continue
                score += self.weights[feature] * numeric_value

        # Normalize to probability
        # Using sigmoid to map score to [0, 1]
        probability = 1 / (1 + math.exp(-score / 10))

        # Classification with confidence
        if probability > 0.7:
            classification = "AI-Generated Code"
        elif probability < 0.3:
            classification = "Human-Written Code"
        else:
            classification = "Uncertain (Mixed Signals)"

        return classification, probability


def analyze_python_code(code: str) -> Tuple[Dict[str, Union[bool, float, int, str]], str]:
    """
    Main analysis function that returns features and classification
    """
    analyzer = ImprovedPythonAnalyzer(code)
    features = analyzer.extract_all_features()

    classifier = ImprovedClassifier()
    classification, confidence = classifier.classify(features)

    # Add confidence to features for API compatibility
    features['confidence'] = confidence

    return features, classification
