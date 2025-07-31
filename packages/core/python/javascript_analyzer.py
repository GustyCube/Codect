import re
import json
import math
from collections import Counter
from typing import Dict, List, Tuple, Union

class ImprovedJavaScriptAnalyzer:
    """
    Enhanced JavaScript analyzer that detects AI-generated patterns
    """

    def __init__(self, code: str):
        self.code = code
        self.lines = code.splitlines()

    def extract_all_features(self) -> Dict[str, Union[bool, float, int, str]]:
        """Extract comprehensive features for classification"""
        features = {}

        # Extract different feature categories
        features.update(self._extract_structural_patterns())
        features.update(self._extract_naming_patterns())
        features.update(self._extract_consistency_metrics())
        features.update(self._extract_code_smell_indicators())
        features.update(self._extract_ai_specific_patterns())
        features.update(self._extract_js_specific_patterns())

        return features

    def _extract_structural_patterns(self) -> Dict[str, Union[bool, float]]:
        """Extract JavaScript structural patterns"""
        features = {
            'uses_arrow_functions': False,
            'uses_async_await': False,
            'uses_destructuring': False,
            'uses_template_literals': False,
            'uses_spread_operator': False,
            'uses_optional_chaining': False,
            'has_iife': False,
            'function_style_consistency': 0.0,
            'import_export_usage': False,
            'uses_strict_mode': False,
        }

        # Arrow functions
        arrow_pattern = re.compile(r'=>')
        features['uses_arrow_functions'] = bool(arrow_pattern.search(self.code))

        # Async/await
        async_pattern = re.compile(r'\basync\s+|await\s+')
        features['uses_async_await'] = bool(async_pattern.search(self.code))

        # Destructuring
        destructure_pattern = re.compile(r'const\s*\{[^}]+\}\s*=|const\s*\[[^\]]+\]\s*=')
        features['uses_destructuring'] = bool(destructure_pattern.search(self.code))

        # Template literals
        template_pattern = re.compile(r'`[^`]*\$\{[^}]+\}[^`]*`')
        features['uses_template_literals'] = bool(template_pattern.search(self.code))

        # Spread operator
        spread_pattern = re.compile(r'\.\.\.')
        features['uses_spread_operator'] = bool(spread_pattern.search(self.code))

        # Optional chaining
        optional_pattern = re.compile(r'\?\.')
        features['uses_optional_chaining'] = bool(optional_pattern.search(self.code))

        # IIFE (Immediately Invoked Function Expression)
        iife_pattern = re.compile(r'\(\s*function\s*\([^)]*\)\s*\{[^}]+\}\s*\)\s*\(')
        features['has_iife'] = bool(iife_pattern.search(self.code))

        # Import/Export
        import_export_pattern = re.compile(r'^\s*(import|export)\s+', re.MULTILINE)
        features['import_export_usage'] = bool(import_export_pattern.search(self.code))

        # Strict mode
        strict_pattern = re.compile(r'["\']use strict["\']')
        features['uses_strict_mode'] = bool(strict_pattern.search(self.code))

        # Function style consistency
        features['function_style_consistency'] = self._calculate_function_consistency()

        return features

    def _extract_naming_patterns(self) -> Dict[str, Union[bool, float]]:
        """Analyze JavaScript naming patterns"""
        features = {
            'uses_camelCase_ratio': 0.0,
            'uses_snake_case_ratio': 0.0,
            'meaningful_name_ratio': 0.0,
            'single_letter_var_ratio': 0.0,
            'avg_name_length': 0.0,
            'uses_dollar_sign': False,
            'uses_underscore_prefix': False,
        }

        # Extract variable and function names
        var_pattern = re.compile(r'(?:var|let|const|function)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)')
        names: List[str] = var_pattern.findall(self.code)

        if not names:
            return features

        # CamelCase vs snake_case
        camelCase_count = sum(1 for name in names if self._is_camelCase(name))
        snake_case_count = sum(1 for name in names if self._is_snake_case(name))

        features['uses_camelCase_ratio'] = camelCase_count / len(names)
        features['uses_snake_case_ratio'] = snake_case_count / len(names)

        # Single letter variables
        single_letter = [n for n in names if len(n) == 1 and n not in 'ijkxy']
        features['single_letter_var_ratio'] = len(single_letter) / len(names)

        # Average name length
        features['avg_name_length'] = sum(len(n) for n in names) / len(names)

        # Meaningful names
        common_meaningless = {'tmp', 'temp', 'var', 'val', 'res', 'ret', 'obj', 'item', 'data', 'arr'}
        meaningful = [n for n in names if len(n) > 3 and n.lower() not in common_meaningless]
        features['meaningful_name_ratio'] = len(meaningful) / len(names)

        # Special naming conventions
        features['uses_dollar_sign'] = any('$' in name for name in names)
        features['uses_underscore_prefix'] = any(name.startswith('_') for name in names)

        return features

    def _extract_consistency_metrics(self) -> Dict[str, float]:
        """Measure JavaScript code consistency"""
        features = {
            'semicolon_consistency': 0.0,
            'quote_consistency': 0.0,
            'indentation_consistency': 0.0,
            'bracket_style_consistency': 0.0,
            'pattern_repetition_score': 0.0,
        }

        # Semicolon consistency
        lines_needing_semicolon = []
        for line in self.lines:
            stripped = line.strip()
            if stripped and not stripped.endswith(('{', '}', ';', ',', '//', '/*', '*/', '*/')) and \
               not stripped.startswith(('//', '/*', '*')):
                lines_needing_semicolon.append(stripped)

        if lines_needing_semicolon:
            with_semicolon = sum(1 for line in lines_needing_semicolon if line.endswith(';'))
            features['semicolon_consistency'] = max(with_semicolon, len(lines_needing_semicolon) - with_semicolon) / len(lines_needing_semicolon)

        # Quote consistency
        single_quotes = len(re.findall(r"'[^']*'", self.code))
        double_quotes = len(re.findall(r'"[^"]*"', self.code))
        backticks = len(re.findall(r'`[^`]*`', self.code))

        total_quotes = single_quotes + double_quotes
        if total_quotes > 0:
            features['quote_consistency'] = max(single_quotes, double_quotes) / total_quotes

        # Indentation consistency
        indents: List[int] = []
        for line in self.lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indents.append(indent)

        if indents:
            # Check if all indents are multiples of 2 or 4
            base_indent = 2 if any(i % 2 == 0 and i % 4 != 0 for i in indents) else 4
            consistent = all(i % base_indent == 0 for i in indents)
            features['indentation_consistency'] = 1.0 if consistent else 0.5

        # Pattern repetition
        features['pattern_repetition_score'] = self._calculate_pattern_repetition()

        return features

    def _extract_code_smell_indicators(self) -> Dict[str, bool]:
        """Detect JavaScript code smells"""
        features = {
            'has_console_log': False,
            'has_debugger': False,
            'has_todo_comments': False,
            'has_commented_code': False,
            'has_alert': False,
            'has_eval': False,
            'has_var_declarations': False,
            'has_magic_strings': False,
            'has_long_lines': False,
            'has_callback_hell': False,
        }

        # Console.log
        console_pattern = re.compile(r'console\.(log|debug|warn|error)')
        features['has_console_log'] = bool(console_pattern.search(self.code))

        # Debugger statements
        debugger_pattern = re.compile(r'\bdebugger\s*;')
        features['has_debugger'] = bool(debugger_pattern.search(self.code))

        # TODO comments
        todo_pattern = re.compile(r'//\s*(TODO|FIXME|HACK|XXX|BUG)', re.IGNORECASE)
        features['has_todo_comments'] = bool(todo_pattern.search(self.code))

        # Commented code
        commented_code_pattern = re.compile(r'//\s*(if|for|while|function|const|let|var|return)\s')
        features['has_commented_code'] = bool(commented_code_pattern.search(self.code))

        # Alert
        alert_pattern = re.compile(r'\balert\s*\(')
        features['has_alert'] = bool(alert_pattern.search(self.code))

        # Eval
        eval_pattern = re.compile(r'\beval\s*\(')
        features['has_eval'] = bool(eval_pattern.search(self.code))

        # Var declarations (vs const/let)
        var_pattern = re.compile(r'\bvar\s+')
        features['has_var_declarations'] = bool(var_pattern.search(self.code))

        # Long lines
        features['has_long_lines'] = any(len(line) > 100 for line in self.lines)

        # Callback hell detection (nested callbacks)
        callback_pattern = re.compile(r'function\s*\([^)]*\)\s*\{[^}]*function\s*\([^)]*\)\s*\{')
        features['has_callback_hell'] = bool(callback_pattern.search(self.code))

        return features

    def _extract_ai_specific_patterns(self) -> Dict[str, Union[bool, float]]:
        """Extract patterns specific to AI-generated JavaScript"""
        features = {
            'perfect_formatting_score': 0.0,
            'generic_example_score': 0.0,
            'placeholder_score': 0.0,
            'uniform_complexity': 0.0,
            'has_example_data': False,
            'excessive_comments_ratio': 0.0,
        }

        # Generic examples
        generic_pattern = re.compile(r'\b(foo|bar|baz|example|test|sample|demo|myFunction|myVariable)\b', re.IGNORECASE)
        generic_matches = len(generic_pattern.findall(self.code))
        features['generic_example_score'] = min(generic_matches / max(len(self.lines), 1), 1.0)

        # Example data
        example_data_pattern = re.compile(r'(John Doe|jane@example\.com|Lorem ipsum|example\.com|123 Main St)')
        features['has_example_data'] = bool(example_data_pattern.search(self.code))

        # Placeholder patterns
        placeholder_pattern = re.compile(r'(Your|TODO:|FIXME:|INSERT|REPLACE|your-|my-)', re.IGNORECASE)
        features['placeholder_score'] = min(len(placeholder_pattern.findall(self.code)) / 10, 1.0)

        # Excessive comments (AI often over-comments)
        comment_lines = sum(1 for line in self.lines if line.strip().startswith('//'))
        if len(self.lines) > 0:
            features['excessive_comments_ratio'] = comment_lines / len(self.lines)

        return features

    def _extract_js_specific_patterns(self) -> Dict[str, Union[bool, str]]:
        """Extract JavaScript-specific patterns"""
        features = {
            'uses_jquery': False,
            'uses_react_patterns': False,
            'uses_node_patterns': False,
            'uses_typescript_patterns': False,
            'has_package_json_refs': False,
            'module_pattern': 'none',  # none, commonjs, es6
        }

        # jQuery
        jquery_pattern = re.compile(r'\$\s*\(|jQuery\s*\(')
        features['uses_jquery'] = bool(jquery_pattern.search(self.code))

        # React patterns
        react_pattern = re.compile(r'(useState|useEffect|React\.|jsx|className=)')
        features['uses_react_patterns'] = bool(react_pattern.search(self.code))

        # Node.js patterns
        node_pattern = re.compile(r'(require\s*\(|module\.exports|process\.|__dirname|__filename)')
        features['uses_node_patterns'] = bool(node_pattern.search(self.code))

        # TypeScript patterns (in comments or JSDoc)
        ts_pattern = re.compile(r'(@param\s*\{|@returns\s*\{|: string|: number|: boolean|interface\s+\w+)')
        features['uses_typescript_patterns'] = bool(ts_pattern.search(self.code))

        # Module pattern detection
        if re.search(r'module\.exports|exports\.', self.code):
            features['module_pattern'] = 'commonjs'
        elif re.search(r'export\s+(default|const|function|class)|import\s+.*\s+from', self.code):
            features['module_pattern'] = 'es6'

        return features

    def _is_camelCase(self, name: str) -> bool:
        """Check if name follows camelCase convention"""
        return bool(re.match(r'^[a-z][a-zA-Z0-9]*$', name))

    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention"""
        return bool(re.match(r'^[a-z_][a-z0-9_]*$', name))

    def _calculate_function_consistency(self) -> float:
        """Calculate consistency in function declaration style"""
        # Count different function styles
        traditional = len(re.findall(r'function\s+\w+\s*\(', self.code))
        arrow = len(re.findall(r'=>', self.code))
        anonymous = len(re.findall(r'function\s*\(', self.code)) - traditional

        total = traditional + arrow + anonymous
        if total == 0:
            return 0.0

        # Higher score means more consistent (one style dominates)
        max_style = max(traditional, arrow, anonymous)
        return max_style / total

    def _calculate_pattern_repetition(self) -> float:
        """Calculate code pattern repetition"""
        # Extract code structure patterns
        patterns: List[str] = []

        # Simple pattern extraction based on keywords
        keyword_pattern = re.compile(r'\b(if|for|while|function|const|let|var|return|class)\b')

        for line in self.lines:
            keywords = keyword_pattern.findall(line)
            if keywords:
                patterns.extend(keywords)

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


class ImprovedJSClassifier:
    """
    Weighted classification system for JavaScript
    """

    def __init__(self):
        # Feature weights based on importance
        self.weights = {
            # Strong AI indicators
            'function_style_consistency': 2.0,
            'semicolon_consistency': 1.5,
            'quote_consistency': 1.5,
            'indentation_consistency': 2.0,
            'pattern_repetition_score': 3.0,
            'generic_example_score': 3.5,
            'placeholder_score': 3.0,
            'has_example_data': 2.5,
            'excessive_comments_ratio': 2.0,

            # Strong human indicators
            'has_console_log': -2.5,
            'has_debugger': -3.0,
            'has_todo_comments': -3.0,
            'has_commented_code': -2.0,
            'has_alert': -2.0,
            'has_eval': -1.5,
            'has_var_declarations': -1.0,
            'has_long_lines': -1.0,
            'has_callback_hell': -1.5,
            'single_letter_var_ratio': -1.0,

            # Context-dependent
            'uses_arrow_functions': 0.3,  # Modern JS
            'uses_async_await': 0.3,
            'uses_destructuring': 0.2,
            'uses_template_literals': 0.2,
            'uses_jquery': -0.5,  # Older human code
            'meaningful_name_ratio': -0.5,
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
        probability = 1 / (1 + math.exp(-score / 10))

        # Classification with confidence
        if probability > 0.7:
            classification = "AI-Generated Code"
        elif probability < 0.3:
            classification = "Human-Written Code"
        else:
            classification = "Uncertain (Mixed Signals)"

        return classification, probability


def analyze_javascript_code(code: str) -> Tuple[Dict[str, Union[bool, float, int, str]], str]:
    """
    Main JavaScript analysis function that returns features and classification
    """
    analyzer = ImprovedJavaScriptAnalyzer(code)
    features = analyzer.extract_all_features()

    classifier = ImprovedJSClassifier()
    classification, confidence = classifier.classify(features)

    # Add confidence to features for API compatibility
    features['confidence'] = confidence

    return features, classification