import io
import math
import re
import tokenize
from collections import Counter
from typing import Dict, Iterable, List, Sequence, Tuple


def clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def saturate(value: float, scale: float) -> float:
    if scale <= 0:
        return 0.0
    return clamp(value / scale)


def sigmoid(value: float) -> float:
    return 1.0 / (1.0 + math.exp(-value))


def std_dev(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance)


def calculate_entropy(tokens: Sequence[str]) -> float:
    if not tokens:
        return 0.0

    counts = Counter(tokens)
    total = len(tokens)
    entropy = 0.0

    for count in counts.values():
        probability = count / total
        entropy -= probability * math.log2(probability)

    return entropy


def tokenize_python(code: str) -> List[str]:
    tokens: List[str] = []

    try:
        readline = io.StringIO(code).readline
        for token_info in tokenize.generate_tokens(readline):
            if token_info.type in (
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.NEWLINE,
                tokenize.NL,
                tokenize.COMMENT,
                tokenize.ENCODING,
            ):
                continue
            if token_info.string:
                tokens.append(token_info.string)
    except tokenize.TokenError:
        return []

    return tokens


def tokenize_generic(code: str) -> List[str]:
    return re.findall(
        r"[A-Za-z_$][A-Za-z0-9_$]*|\d+(?:\.\d+)?|==|!=|<=|>=|=>|\.\.\.|[{}()[\].,;:+\-*/%<>!?=]",
        code,
    )


def build_text_metrics(code: str, tokens: Sequence[str], comment_lines: int) -> Dict[str, float]:
    lines = code.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    trimmed_lengths = [len(line.rstrip()) for line in non_empty_lines]

    avg_line_length = safe_ratio(sum(trimmed_lengths), len(trimmed_lengths))
    length_variance = std_dev([float(length) for length in trimmed_lengths]) if trimmed_lengths else 0.0

    return {
        "total_lines": len(lines),
        "non_empty_lines": len(non_empty_lines),
        "blank_line_ratio": safe_ratio(len(lines) - len(non_empty_lines), len(lines)),
        "token_count": len(tokens),
        "token_entropy": calculate_entropy(tokens),
        "comment_ratio": safe_ratio(comment_lines, len(lines)),
        "avg_line_length": avg_line_length,
        "line_length_variance": length_variance,
        "line_length_uniformity": 1.0 - clamp(safe_ratio(length_variance, avg_line_length or 1.0)),
    }


def dominant_ratio(values: Iterable[int]) -> float:
    items = [value for value in values if value > 0]
    total = sum(items)
    if total == 0:
        return 0.0
    return max(items) / total


def indentation_consistency(lines: Sequence[str], preferred_widths: Sequence[int] = (2, 4)) -> float:
    indent_levels = []

    for line in lines:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent > 0:
            indent_levels.append(indent)

    if not indent_levels:
        return 0.0

    scores = []
    for width in preferred_widths:
        consistent = sum(1 for indent in indent_levels if indent % width == 0)
        scores.append(consistent / len(indent_levels))

    return max(scores)


def quote_consistency_from_strings(strings: Sequence[str]) -> float:
    quote_counts = Counter()

    for token in strings:
        if len(token) < 2:
            continue
        if token[0] in ("'", '"', "`"):
            quote_counts[token[0]] += 1

    total = sum(quote_counts.values())
    if total == 0:
        return 0.0

    return max(quote_counts.values()) / total


def pattern_repetition(sequence: Sequence[str], window: int = 3) -> float:
    if len(sequence) < window:
        return 0.0

    counts = Counter(tuple(sequence[index:index + window]) for index in range(len(sequence) - window + 1))
    total_windows = len(sequence) - window + 1
    return max(counts.values()) / total_windows


def normalized_count(value: int, scale: float) -> float:
    return saturate(float(value), scale)


def classify_signals(
    features: Dict[str, object],
    ai_weights: Dict[str, float],
    human_weights: Dict[str, float],
    *,
    minimum_lines: int = 5,
    minimum_tokens: int = 24,
    minimum_signal: float = 1.2,
    minimum_margin: float = 0.8,
) -> Tuple[str, float, float]:
    ai_score = 0.0
    human_score = 0.0
    ai_contributions = []
    human_contributions = []

    for name, weight in ai_weights.items():
        value = features.get(name, 0.0)
        if isinstance(value, bool):
            numeric = 1.0 if value else 0.0
        elif isinstance(value, (int, float)):
            numeric = float(value)
        else:
            continue

        contribution = numeric * weight
        ai_score += contribution
        if contribution > 0.0:
            ai_contributions.append((contribution, name))

    for name, weight in human_weights.items():
        value = features.get(name, 0.0)
        if isinstance(value, bool):
            numeric = 1.0 if value else 0.0
        elif isinstance(value, (int, float)):
            numeric = float(value)
        else:
            continue

        contribution = numeric * weight
        human_score += contribution
        if contribution > 0.0:
            human_contributions.append((contribution, name))

    score_gap = ai_score - human_score
    signal_strength = ai_score + human_score
    ai_probability = sigmoid(score_gap)

    line_count = int(features.get("non_empty_lines", 0) or 0)
    token_count = int(features.get("token_count", 0) or 0)
    margin = abs(score_gap)

    low_signal = (
        line_count < minimum_lines
        or token_count < minimum_tokens
        or signal_strength < minimum_signal
        or margin < minimum_margin
    )

    if low_signal:
        classification = "Uncertain (Mixed Signals)"
    elif score_gap > 0:
        classification = "AI-Generated Code"
    else:
        classification = "Human-Written Code"

    confidence = 0.5 + 0.5 * clamp((margin / 3.0) * min(signal_strength / 4.0, 1.0))

    features["ai_score"] = round(ai_score, 4)
    features["human_score"] = round(human_score, 4)
    features["score_gap"] = round(score_gap, 4)
    features["signal_strength"] = round(signal_strength, 4)
    features["ai_probability"] = round(ai_probability, 4)
    features["confidence"] = round(confidence, 4)
    features["top_ai_signals"] = [
        name.replace("_", " ")
        for _, name in sorted(ai_contributions, reverse=True)[:3]
    ]
    features["top_human_signals"] = [
        name.replace("_", " ")
        for _, name in sorted(human_contributions, reverse=True)[:3]
    ]

    if line_count < minimum_lines or token_count < minimum_tokens:
        features["decision_basis"] = "low-signal snippet"
    elif signal_strength < minimum_signal or margin < minimum_margin:
        features["decision_basis"] = "conflicting heuristics"
    else:
        features["decision_basis"] = "clear heuristic signal"

    return classification, ai_probability, confidence


def split_code_into_chunks(code: str, target_chars: int = 2200, minimum_tail_chars: int = 500) -> List[str]:
    lines = code.splitlines(keepends=True)
    if not lines:
        return [code]

    chunks: List[str] = []
    current_lines: List[str] = []
    current_length = 0

    for line in lines:
        if current_lines and current_length + len(line) > target_chars:
            chunks.append("".join(current_lines).strip("\n"))
            current_lines = [line]
            current_length = len(line)
        else:
            current_lines.append(line)
            current_length += len(line)

    if current_lines:
        chunks.append("".join(current_lines).strip("\n"))

    if len(chunks) > 1 and len(chunks[-1]) < minimum_tail_chars:
        chunks[-2] = chunks[-2] + "\n" + chunks[-1]
        chunks.pop()

    return [chunk for chunk in chunks if chunk.strip()] or [code]


def aggregate_chunk_results(
    chunk_results: Sequence[Tuple[Dict[str, object], str]]
) -> Tuple[Dict[str, object], str]:
    if len(chunk_results) == 1:
        features = dict(chunk_results[0][0])
        features["chunk_count"] = 1
        features["clear_chunk_count"] = 1 if features.get("decision_basis") == "clear heuristic signal" else 0
        features["chunk_classifications"] = [chunk_results[0][1]]
        return features, chunk_results[0][1]

    sum_fields = {
        "total_lines",
        "non_empty_lines",
        "token_count",
        "function_count",
        "loop_count",
        "try_except_count",
    }
    max_fields = {"max_ast_depth"}

    aggregate: Dict[str, object] = {}
    chunk_classifications = [classification for _, classification in chunk_results]
    clear_chunk_count = sum(
        1 for features, _ in chunk_results if features.get("decision_basis") == "clear heuristic signal"
    )

    weights = []
    for features, _ in chunk_results:
        signal_strength = float(features.get("signal_strength", 0.0) or 0.0)
        non_empty_lines = float(features.get("non_empty_lines", 0) or 0)
        weights.append(max(signal_strength, 0.5) * max(non_empty_lines, 1.0))

    total_weight = sum(weights) or float(len(chunk_results))
    numeric_keys = {
        key
        for features, _ in chunk_results
        for key, value in features.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }

    for key in numeric_keys:
        values = [float(features.get(key, 0.0) or 0.0) for features, _ in chunk_results]
        if key in sum_fields:
            aggregate[key] = round(sum(values), 4)
        elif key in max_fields:
            aggregate[key] = round(max(values), 4)
        else:
            aggregate[key] = round(
                sum(value * weight for value, weight in zip(values, weights)) / total_weight,
                4,
            )

    bool_keys = {
        key
        for features, _ in chunk_results
        for key, value in features.items()
        if isinstance(value, bool)
    }
    for key in bool_keys:
        aggregate[key] = any(bool(features.get(key, False)) for features, _ in chunk_results)

    ai_signal_counter = Counter()
    human_signal_counter = Counter()

    for features, _ in chunk_results:
        for value in features.get("top_ai_signals", []):
            ai_signal_counter[str(value)] += 1
        for value in features.get("top_human_signals", []):
            human_signal_counter[str(value)] += 1

    weighted_gap = aggregate.get("score_gap", 0.0)
    ai_probability = aggregate.get("ai_probability", 0.5)

    if clear_chunk_count == 0 or abs(float(weighted_gap)) < 0.75:
        classification = "Uncertain (Mixed Signals)"
    elif float(ai_probability) >= 0.65:
        classification = "AI-Generated Code"
    elif float(ai_probability) <= 0.35:
        classification = "Human-Written Code"
    else:
        classification = "Uncertain (Mixed Signals)"

    aggregate["chunk_count"] = len(chunk_results)
    aggregate["clear_chunk_count"] = clear_chunk_count
    aggregate["chunk_classifications"] = chunk_classifications
    aggregate["top_ai_signals"] = [name for name, _ in ai_signal_counter.most_common(3)]
    aggregate["top_human_signals"] = [name for name, _ in human_signal_counter.most_common(3)]
    aggregate["decision_basis"] = (
        "chunk-level aggregation" if clear_chunk_count > 0 else "low-signal snippet"
    )

    return aggregate, classification
