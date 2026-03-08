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
    tokenize_generic,
)


FeatureValue = Union[bool, float, int, str, List[str]]


class ImprovedJavaScriptAnalyzer:
    """JavaScript feature extractor for heuristic AI-vs-human scoring."""

    AI_WEIGHTS = {
        "generic_example_score": 1.5,
        "example_usage_score": 1.2,
        "placeholder_score": 1.0,
        "excessive_comments_ratio": 0.7,
        "function_style_consistency": 0.5,
        "semicolon_consistency": 0.4,
        "indentation_consistency": 0.4,
        "quote_consistency": 0.3,
        "pattern_repetition_score": 0.7,
        "line_length_uniformity": 0.3,
    }

    HUMAN_WEIGHTS = {
        "todo_comment_score": 1.6,
        "debugger_score": 1.4,
        "commented_code_score": 1.1,
        "alert_score": 0.9,
        "eval_score": 0.8,
        "var_declaration_score": 0.7,
        "callback_hell_score": 0.9,
        "jquery_score": 0.9,
        "console_log_score": 0.6,
        "single_letter_var_ratio": 0.4,
        "long_line_score": 0.4,
    }

    def __init__(self, code: str):
        self.code = code
        self.lines = code.splitlines()
        self.tokens = tokenize_generic(code)
        self.comment_lines = self._count_comment_lines()

    def extract_all_features(self) -> Dict[str, FeatureValue]:
        features: Dict[str, FeatureValue] = {
            "function_count": self._count_functions(),
            "loop_count": self._count_loops(),
            "try_except_count": self._count_try_blocks(),
            "max_ast_depth": self._calculate_brace_depth(),
        }

        features.update(build_text_metrics(self.code, self.tokens, self.comment_lines))
        features.update(self._extract_structural_patterns())
        features.update(self._extract_naming_patterns())
        features.update(self._extract_consistency_metrics())
        features.update(self._extract_code_smell_indicators())
        features.update(self._extract_ai_specific_patterns())
        features.update(self._extract_js_specific_patterns())

        return features

    def _extract_structural_patterns(self) -> Dict[str, FeatureValue]:
        return {
            "uses_arrow_functions": "=>" in self.code,
            "uses_async_await": bool(re.search(r"\basync\b|\bawait\b", self.code)),
            "uses_destructuring": bool(re.search(r"(?:const|let)\s*[{[][^}\]]+[}\]]\s*=", self.code)),
            "uses_template_literals": bool(re.search(r"`[^`]*\$\{[^}]+\}", self.code)),
            "uses_spread_operator": "..." in self.code,
            "uses_optional_chaining": "?." in self.code,
            "has_iife": bool(re.search(r"\(\s*function\s*\([^)]*\)\s*{", self.code)),
            "import_export_usage": bool(re.search(r"^\s*(import|export)\s+", self.code, re.MULTILINE)),
            "uses_strict_mode": bool(re.search(r'["\']use strict["\']', self.code)),
            "function_style_consistency": self._calculate_function_consistency(),
            "pattern_repetition_score": pattern_repetition(
                re.findall(r"\b(if|for|while|function|const|let|var|return|class|try|catch)\b", self.code)
            ),
        }

    def _extract_naming_patterns(self) -> Dict[str, FeatureValue]:
        names = re.findall(
            r"(?:var|let|const|function|class)\s+([A-Za-z_$][A-Za-z0-9_$]*)",
            self.code,
        )
        names.extend(re.findall(r"\b([A-Za-z_$][A-Za-z0-9_$]*)\s*=>", self.code))

        if not names:
            return {
                "uses_camel_case_ratio": 0.0,
                "uses_snake_case_ratio": 0.0,
                "meaningful_name_ratio": 0.0,
                "single_letter_var_ratio": 0.0,
                "avg_name_length": 0.0,
                "naming_consistency_score": 0.0,
            }

        camel_case_count = sum(1 for name in names if self._is_camel_case(name))
        snake_case_count = sum(1 for name in names if self._is_snake_case(name))
        plain_lower_count = sum(1 for name in names if name.islower() and "_" not in name and "$" not in name)
        meaningful_names = [
            name
            for name in names
            if len(name) > 3 and name.lower() not in {"tmp", "temp", "var", "val", "res", "ret", "obj", "item", "data", "arr"}
        ]
        single_letter_names = [name for name in names if len(name) == 1 and name not in "ijkxy"]

        return {
            "uses_camel_case_ratio": camel_case_count / len(names),
            "uses_snake_case_ratio": snake_case_count / len(names),
            "meaningful_name_ratio": len(meaningful_names) / len(names),
            "single_letter_var_ratio": len(single_letter_names) / len(names),
            "avg_name_length": sum(len(name) for name in names) / len(names),
            "naming_consistency_score": dominant_ratio(
                [camel_case_count, snake_case_count, plain_lower_count]
            ),
        }

    def _extract_consistency_metrics(self) -> Dict[str, FeatureValue]:
        string_tokens = re.findall(r"'[^'\n]*'|\"[^\"\n]*\"|`[^`\n]*`", self.code)

        semicolon_candidates = []
        for line in self.lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("//", "/*", "*")):
                continue
            if stripped.endswith(("{", "}", ",", ":", ";")):
                continue
            semicolon_candidates.append(stripped)

        with_semicolon = sum(1 for line in semicolon_candidates if line.endswith(";"))
        semicolon_consistency = (
            max(with_semicolon, len(semicolon_candidates) - with_semicolon) / len(semicolon_candidates)
            if semicolon_candidates
            else 0.0
        )

        return {
            "semicolon_consistency": semicolon_consistency,
            "quote_consistency": quote_consistency_from_strings(string_tokens),
            "indentation_consistency": indentation_consistency(self.lines),
        }

    def _extract_code_smell_indicators(self) -> Dict[str, FeatureValue]:
        console_count = len(re.findall(r"console\.(log|debug|warn|error)\s*\(", self.code))
        debugger_count = len(re.findall(r"\bdebugger\b", self.code))
        todo_count = len(re.findall(r"//\s*(TODO|FIXME|HACK|XXX|BUG)\b", self.code, re.IGNORECASE))
        commented_code_count = len(
            re.findall(r"//\s*(if|for|while|function|const|let|var|return|class)\b", self.code)
        )
        alert_count = len(re.findall(r"\balert\s*\(", self.code))
        eval_count = len(re.findall(r"\beval\s*\(", self.code))
        var_count = len(re.findall(r"\bvar\s+", self.code))
        jquery_count = len(re.findall(r"\$\s*\(|jQuery\s*\(", self.code))
        jquery_count += len(re.findall(r"require\s*\(\s*[\"']jquery[\"']\s*\)", self.code))
        callback_hell_count = len(
            re.findall(r"function\s*\([^)]*\)\s*{[^{}]*function\s*\([^)]*\)\s*{", self.code, re.DOTALL)
        )
        long_line_count = sum(1 for line in self.lines if len(line.rstrip()) > 100)

        return {
            "has_console_log": console_count > 0,
            "has_debugger": debugger_count > 0,
            "has_todo_comments": todo_count > 0,
            "has_commented_code": commented_code_count > 0,
            "has_alert": alert_count > 0,
            "has_eval": eval_count > 0,
            "has_var_declarations": var_count > 0,
            "has_long_lines": long_line_count > 0,
            "has_callback_hell": callback_hell_count > 0,
            "uses_jquery": jquery_count > 0,
            "console_log_score": normalized_count(console_count, 3.0),
            "debugger_score": normalized_count(debugger_count, 1.0),
            "todo_comment_score": normalized_count(todo_count, 2.0),
            "commented_code_score": normalized_count(commented_code_count, 2.0),
            "alert_score": normalized_count(alert_count, 1.0),
            "eval_score": normalized_count(eval_count, 1.0),
            "var_declaration_score": normalized_count(var_count, 3.0),
            "callback_hell_score": normalized_count(callback_hell_count, 1.0),
            "jquery_score": normalized_count(jquery_count, 1.0),
            "long_line_score": normalized_count(long_line_count, 3.0),
        }

    def _extract_ai_specific_patterns(self) -> Dict[str, FeatureValue]:
        generic_matches = len(
            re.findall(r"\b(foo|bar|baz|example|sample|demo|tutorial|helper|myFunction|myVariable)\b", self.code, re.IGNORECASE)
        )
        example_usage_matches = len(
            re.findall(r"\b(example|sample|demo|mock)(?:Data|Input|Output)?\b|example usage", self.code, re.IGNORECASE)
        )
        placeholder_matches = len(
            re.findall(r"\b(TODO|FIXME|INSERT|REPLACE|your-|my-)\b", self.code, re.IGNORECASE)
        )
        line_comments = sum(1 for line in self.lines if line.strip().startswith("//"))

        return {
            "generic_example_score": normalized_count(generic_matches, 3.0),
            "example_usage_score": normalized_count(example_usage_matches, 4.0),
            "placeholder_score": normalized_count(placeholder_matches, 3.0),
            "excessive_comments_ratio": saturate(line_comments, 5.0) * saturate(float(line_comments), max(len(self.lines), 1)),
        }

    def _extract_js_specific_patterns(self) -> Dict[str, FeatureValue]:
        module_pattern = "none"
        if re.search(r"module\.exports|exports\.", self.code):
            module_pattern = "commonjs"
        elif re.search(r"export\s+(default|const|function|class)|import\s+.*\s+from", self.code):
            module_pattern = "es6"

        return {
            "uses_react_patterns": bool(re.search(r"(useState|useEffect|React\.|jsx|className=)", self.code)),
            "uses_node_patterns": bool(re.search(r"(require\s*\(|module\.exports|process\.|__dirname|__filename)", self.code)),
            "uses_typescript_patterns": bool(
                re.search(r"(@param\s*{|@returns\s*{|:\s*(string|number|boolean)|interface\s+\w+)", self.code)
            ),
            "module_pattern": module_pattern,
        }

    def _count_comment_lines(self) -> int:
        count = 0
        in_block_comment = False

        for line in self.lines:
            stripped = line.strip()
            if not stripped:
                continue

            if in_block_comment:
                count += 1
                if "*/" in stripped:
                    in_block_comment = False
                continue

            if stripped.startswith("//"):
                count += 1
                continue

            if stripped.startswith("/*"):
                count += 1
                if "*/" not in stripped:
                    in_block_comment = True

        return count

    def _count_functions(self) -> int:
        named_functions = len(re.findall(r"\bfunction\b", self.code))
        arrow_functions = len(re.findall(r"=>", self.code))
        return named_functions + arrow_functions

    def _count_loops(self) -> int:
        return len(re.findall(r"\b(for|while|do)\b", self.code))

    def _count_try_blocks(self) -> int:
        return len(re.findall(r"\btry\b", self.code))

    def _calculate_function_consistency(self) -> float:
        traditional = len(re.findall(r"\bfunction\s+\w+\s*\(", self.code))
        anonymous = len(re.findall(r"\bfunction\s*\(", self.code)) - traditional
        arrow = len(re.findall(r"=>", self.code))
        return dominant_ratio([traditional, anonymous, arrow])

    def _calculate_brace_depth(self) -> int:
        depth = 0
        max_depth = 0
        in_single = False
        in_double = False
        in_backtick = False
        in_line_comment = False
        in_block_comment = False
        previous = ""

        for index, char in enumerate(self.code):
            next_char = self.code[index + 1] if index + 1 < len(self.code) else ""

            if in_line_comment:
                if char == "\n":
                    in_line_comment = False
                previous = char
                continue

            if in_block_comment:
                if previous == "*" and char == "/":
                    in_block_comment = False
                previous = char
                continue

            if not in_single and not in_double and not in_backtick:
                if char == "/" and next_char == "/":
                    in_line_comment = True
                    previous = char
                    continue
                if char == "/" and next_char == "*":
                    in_block_comment = True
                    previous = char
                    continue

            if char == "'" and not in_double and not in_backtick and previous != "\\":
                in_single = not in_single
            elif char == '"' and not in_single and not in_backtick and previous != "\\":
                in_double = not in_double
            elif char == "`" and not in_single and not in_double and previous != "\\":
                in_backtick = not in_backtick
            elif not in_single and not in_double and not in_backtick:
                if char == "{":
                    depth += 1
                    max_depth = max(max_depth, depth)
                elif char == "}":
                    depth = max(depth - 1, 0)

            previous = char

        return max_depth

    @staticmethod
    def _is_camel_case(name: str) -> bool:
        return bool(re.match(r"^[a-z][a-zA-Z0-9]*$", name)) and "_" not in name

    @staticmethod
    def _is_snake_case(name: str) -> bool:
        return bool(re.match(r"^[a-z_][a-z0-9_]*$", name))


def analyze_javascript_code(code: str) -> Tuple[Dict[str, FeatureValue], str]:
    chunk_results = []

    for chunk in split_code_into_chunks(code):
        analyzer = ImprovedJavaScriptAnalyzer(chunk)
        features = analyzer.extract_all_features()
        classification, _, _ = classify_signals(
            features,
            ImprovedJavaScriptAnalyzer.AI_WEIGHTS,
            ImprovedJavaScriptAnalyzer.HUMAN_WEIGHTS,
        )
        chunk_results.append((features, classification))

    return aggregate_chunk_results(chunk_results)
