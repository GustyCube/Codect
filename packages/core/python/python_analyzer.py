import ast
import re
from typing import Dict, List, Tuple, Union

from common_metrics import (
    aggregate_chunk_results,
    build_text_metrics,
    classify_signals,
    dominant_ratio,
    indentation_consistency,
    normalized_count,
    pattern_repetition,
    quote_consistency_from_strings,
    saturate,
    split_code_into_chunks,
    std_dev,
    tokenize_python,
)


FeatureValue = Union[bool, float, int, str, List[str]]


class ImprovedPythonAnalyzer:
    """Python feature extractor for heuristic AI-vs-human scoring."""

    AI_WEIGHTS = {
        "generic_example_score": 1.5,
        "example_usage_score": 1.1,
        "placeholder_score": 1.0,
        "over_explanation_score": 0.9,
        "docstring_coverage": 0.6,
        "import_organization_score": 0.5,
        "pattern_repetition_score": 0.7,
        "indentation_consistency": 0.4,
        "quote_consistency": 0.3,
        "naming_consistency_score": 0.4,
        "line_length_uniformity": 0.3,
    }

    HUMAN_WEIGHTS = {
        "todo_comment_score": 1.6,
        "debug_print_score": 1.2,
        "commented_code_score": 1.1,
        "magic_number_score": 0.6,
        "trailing_whitespace_score": 1.0,
        "single_letter_var_ratio": 0.4,
        "function_length_variance_score": 0.6,
        "bare_except_score": 1.0,
        "long_line_score": 0.4,
    }

    def __init__(self, code: str):
        self.code = code
        self.lines = code.splitlines()
        self.tree = None
        self.tokens = tokenize_python(code)

        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = None

    def extract_all_features(self) -> Dict[str, FeatureValue]:
        features: Dict[str, FeatureValue] = {
            "parseable": self.tree is not None,
            "function_count": 0,
            "loop_count": 0,
            "try_except_count": 0,
            "max_ast_depth": 0,
        }

        comment_lines = sum(1 for line in self.lines if line.strip().startswith("#"))
        features.update(build_text_metrics(self.code, self.tokens, comment_lines))

        if self.tree is not None:
            features.update(self._extract_ast_metrics())
            features.update(self._extract_structural_patterns())
            features.update(self._extract_naming_patterns())
        else:
            features.update(
                {
                    "has_main_guard": False,
                    "has_docstrings": False,
                    "docstring_coverage": 0.0,
                    "uses_comprehensions": False,
                    "uses_walrus_operator": False,
                    "uses_f_strings": False,
                    "uses_type_hints": False,
                    "import_organization_score": 0.0,
                    "nested_function_depth": 0,
                    "function_length_variance": 0.0,
                    "function_length_variance_score": 0.0,
                    "naming_consistency_score": 0.0,
                    "uses_snake_case_ratio": 0.0,
                    "meaningful_name_ratio": 0.0,
                    "single_letter_var_ratio": 0.0,
                    "avg_name_length": 0.0,
                    "pattern_repetition_score": 0.0,
                }
            )

        features.update(self._extract_consistency_metrics())
        features.update(self._extract_code_smell_indicators())
        features.update(self._extract_ai_specific_patterns())

        return features

    def _extract_ast_metrics(self) -> Dict[str, FeatureValue]:
        assert self.tree is not None

        function_count = 0
        loop_count = 0
        try_except_count = 0

        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_count += 1
            elif isinstance(node, (ast.For, ast.While, ast.AsyncFor)):
                loop_count += 1
            elif isinstance(node, ast.Try):
                try_except_count += 1

        return {
            "function_count": function_count,
            "loop_count": loop_count,
            "try_except_count": try_except_count,
            "max_ast_depth": self._calculate_max_depth(self.tree),
        }

    def _extract_structural_patterns(self) -> Dict[str, FeatureValue]:
        assert self.tree is not None

        functions = [node for node in ast.walk(self.tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        documented_functions = sum(1 for node in functions if ast.get_docstring(node))
        function_lengths = [self._function_length(node) for node in functions]
        statement_patterns = [type(node).__name__ for node in ast.walk(self.tree) if isinstance(node, ast.stmt)]

        return {
            "has_main_guard": any(isinstance(node, ast.If) and self._is_main_guard(node) for node in ast.walk(self.tree)),
            "has_docstrings": documented_functions > 0,
            "docstring_coverage": documented_functions / len(functions) if functions else 0.0,
            "uses_comprehensions": any(
                isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp))
                for node in ast.walk(self.tree)
            ),
            "uses_walrus_operator": any(isinstance(node, ast.NamedExpr) for node in ast.walk(self.tree)),
            "uses_f_strings": any(isinstance(node, ast.JoinedStr) for node in ast.walk(self.tree)),
            "uses_type_hints": any(
                isinstance(node, ast.arg) and node.annotation is not None for node in ast.walk(self.tree)
            )
            or any(
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns is not None
                for node in ast.walk(self.tree)
            ),
            "import_organization_score": self._analyze_import_organization(),
            "nested_function_depth": self._nested_function_depth(self.tree),
            "function_length_variance": std_dev([float(length) for length in function_lengths]),
            "function_length_variance_score": saturate(
                std_dev([float(length) for length in function_lengths]),
                10.0,
            ),
            "pattern_repetition_score": pattern_repetition(statement_patterns),
        }

    def _extract_naming_patterns(self) -> Dict[str, FeatureValue]:
        assert self.tree is not None

        names = self._collect_names()
        if not names:
            return {
                "naming_consistency_score": 0.0,
                "uses_snake_case_ratio": 0.0,
                "meaningful_name_ratio": 0.0,
                "single_letter_var_ratio": 0.0,
                "avg_name_length": 0.0,
            }

        snake_case_count = sum(1 for name in names if self._is_snake_case(name))
        lower_case_count = sum(1 for name in names if name.islower() and "_" not in name)
        upper_case_count = sum(1 for name in names if name.isupper())
        common_meaningless = {"tmp", "temp", "var", "val", "res", "ret", "obj", "item", "data"}
        meaningful_names = [name for name in names if len(name) > 3 and name.lower() not in common_meaningless]
        single_letter_names = [name for name in names if len(name) == 1 and name not in "ijkxyz"]

        return {
            "naming_consistency_score": dominant_ratio(
                [snake_case_count, lower_case_count, upper_case_count]
            ),
            "uses_snake_case_ratio": snake_case_count / len(names),
            "meaningful_name_ratio": len(meaningful_names) / len(names),
            "single_letter_var_ratio": len(single_letter_names) / len(names),
            "avg_name_length": sum(len(name) for name in names) / len(names),
        }

    def _extract_consistency_metrics(self) -> Dict[str, FeatureValue]:
        strings = [token for token in self.tokens if token and token[0] in ("'", '"')]

        return {
            "indentation_consistency": indentation_consistency(self.lines, (4,)),
            "quote_consistency": quote_consistency_from_strings(strings),
        }

    def _extract_code_smell_indicators(self) -> Dict[str, FeatureValue]:
        todo_count = len(re.findall(r"#\s*(TODO|FIXME|HACK|XXX|BUG|REFACTOR)\b", self.code, re.IGNORECASE))
        debug_count = len(re.findall(r"\b(print|breakpoint)\s*\(", self.code))
        commented_code_count = len(
            re.findall(r"#\s*(if|for|while|def|class|import|return|with)\b", self.code)
        )
        trailing_whitespace_count = sum(1 for line in self.lines if line.rstrip() != line)
        long_line_count = sum(1 for line in self.lines if len(line.rstrip()) > 100)

        magic_numbers = 0
        bare_excepts = 0

        if self.tree is not None:
            for node in ast.walk(self.tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    if node.value not in (0, 1, 2, -1, 10, 60, 100, 1000):
                        magic_numbers += 1
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    bare_excepts += 1

        return {
            "has_todo_comments": todo_count > 0,
            "has_debug_prints": debug_count > 0,
            "has_commented_code": commented_code_count > 0,
            "has_magic_numbers": magic_numbers > 0,
            "has_long_lines": long_line_count > 0,
            "has_trailing_whitespace": trailing_whitespace_count > 0,
            "todo_comment_score": normalized_count(todo_count, 2.0),
            "debug_print_score": normalized_count(debug_count, 2.0),
            "commented_code_score": normalized_count(commented_code_count, 2.0),
            "magic_number_score": normalized_count(magic_numbers, 6.0),
            "long_line_score": normalized_count(long_line_count, 3.0),
            "trailing_whitespace_score": normalized_count(trailing_whitespace_count, 2.0),
            "bare_except_score": normalized_count(bare_excepts, 2.0),
        }

    def _extract_ai_specific_patterns(self) -> Dict[str, FeatureValue]:
        comment_lines = [line.strip() for line in self.lines if line.strip().startswith("#")]
        average_comment_length = (
            sum(len(line) for line in comment_lines) / len(comment_lines)
            if comment_lines
            else 0.0
        )

        generic_matches = len(
            re.findall(r"\b(foo|bar|baz|example|sample|demo|tutorial|helper)\b", self.code, re.IGNORECASE)
        )
        example_usage_matches = len(
            re.findall(r"\b(example|sample|demo)_?\w*\b|example usage", self.code, re.IGNORECASE)
        )
        placeholder_matches = len(
            re.findall(r"\b(TODO|FIXME|INSERT|REPLACE|your_|my_|some_)\b", self.code, re.IGNORECASE)
        )

        return {
            "generic_example_score": normalized_count(generic_matches, 3.0),
            "example_usage_score": normalized_count(example_usage_matches, 4.0),
            "placeholder_score": normalized_count(placeholder_matches, 3.0),
            "over_explanation_score": saturate(average_comment_length, 70.0)
            * saturate(float(len(comment_lines)), 4.0),
        }

    def _collect_names(self) -> List[str]:
        assert self.tree is not None

        names: List[str] = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name):
                names.append(node.id)
            elif isinstance(node, ast.arg):
                names.append(node.arg)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.append(node.name)

        return names

    def _analyze_import_organization(self) -> float:
        import_lines: List[Tuple[int, str]] = []

        for index, line in enumerate(self.lines):
            stripped = line.strip()
            if stripped.startswith(("import ", "from ")):
                import_lines.append((index, stripped))

        if len(import_lines) < 2:
            return 0.0

        groups = []
        current_group = [import_lines[0]]

        for index in range(1, len(import_lines)):
            current = import_lines[index]
            previous = import_lines[index - 1]
            if current[0] - previous[0] == 1:
                current_group.append(current)
            else:
                groups.append(current_group)
                current_group = [current]
        groups.append(current_group)

        sorted_groups = 0
        for group in groups:
            values = [line for _, line in group]
            if values == sorted(values):
                sorted_groups += 1

        return sorted_groups / len(groups)

    def _function_length(self, function_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> int:
        end_lineno = getattr(function_node, "end_lineno", None)
        if end_lineno is not None:
            return max(end_lineno - function_node.lineno + 1, 1)
        return max(len(function_node.body), 1)

    def _nested_function_depth(self, node: ast.AST, depth: int = 0) -> int:
        child_depths = []
        for child in ast.iter_child_nodes(node):
            child_depth = depth
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                child_depth += 1
            child_depths.append(self._nested_function_depth(child, child_depth))

        return max([depth] + child_depths)

    def _calculate_max_depth(self, node: ast.AST, depth: int = 0) -> int:
        child_depths = [self._calculate_max_depth(child, depth + 1) for child in ast.iter_child_nodes(node)]
        return max([depth] + child_depths)

    @staticmethod
    def _is_main_guard(node: ast.If) -> bool:
        if not isinstance(node.test, ast.Compare):
            return False
        if not isinstance(node.test.left, ast.Name) or node.test.left.id != "__name__":
            return False
        if not any(isinstance(operator, ast.Eq) for operator in node.test.ops):
            return False
        return any(
            isinstance(comparator, ast.Constant) and comparator.value == "__main__"
            for comparator in node.test.comparators
        )

    @staticmethod
    def _is_snake_case(name: str) -> bool:
        return bool(re.match(r"^[a-z_][a-z0-9_]*$", name))


def analyze_python_code(code: str) -> Tuple[Dict[str, FeatureValue], str]:
    chunk_results = []

    for chunk in split_code_into_chunks(code):
        analyzer = ImprovedPythonAnalyzer(chunk)
        features = analyzer.extract_all_features()
        classification, _, _ = classify_signals(
            features,
            ImprovedPythonAnalyzer.AI_WEIGHTS,
            ImprovedPythonAnalyzer.HUMAN_WEIGHTS,
        )
        chunk_results.append((features, classification))

    return aggregate_chunk_results(chunk_results)
