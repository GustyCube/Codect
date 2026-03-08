import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = ROOT / "python"
sys.path.insert(0, str(PYTHON_DIR))

from javascript_analyzer import analyze_javascript_code  # noqa: E402
from python_analyzer import analyze_python_code  # noqa: E402


AI_PYTHON = """
def normalize_example_records(example_records):
    \"\"\"Normalize example records and return a predictable summary.\"\"\"
    normalized_records = []

    for example_record in example_records:
        normalized_record = {
            "name": example_record["name"].strip().title(),
            "score": round(example_record["score"], 2),
        }
        normalized_records.append(normalized_record)

    return normalized_records


def main():
    sample_records = [
        {"name": "alice", "score": 98.125},
        {"name": "bob", "score": 91.437},
    ]
    normalized_records = normalize_example_records(sample_records)

    for normalized_record in normalized_records:
        print(normalized_record)


if __name__ == "__main__":
    main()
"""


HUMAN_PYTHON = """
import os


# TODO: clean this up when the CSV export is fixed
def load_names(input_file):
    names = []

    try:
        with open(input_file, "r") as handle:
            for raw_line in handle:
                value = raw_line.strip()
                if value:
                    names.append(value)
    except:
        print("debug: missing file")
        return []

    # old parsing branch
    # if value.startswith("#"):
    #     continue
    if len(names) > 42:
        print("too many names")

    return names
"""


AI_JAVASCRIPT = """
function buildExampleSummary(exampleItems) {
  return exampleItems.map((exampleItem) => {
    const normalizedName = exampleItem.name.trim().toUpperCase();
    return {
      id: exampleItem.id,
      displayName: `${normalizedName} (${exampleItem.status})`,
    };
  });
}

const sampleItems = [
  { id: 1, name: "alpha", status: "ready" },
  { id: 2, name: "beta", status: "pending" },
];

const exampleSummary = buildExampleSummary(sampleItems);
"""


HUMAN_JAVASCRIPT = """
var config = require("./config");
const $ = require("jquery");

// TODO: stop doing this once the real API ships
function getData() {
  var result;
  console.log("fetching data...");

  $.ajax({
    url: config.endpoint,
    success: function(data) {
      result = data;
      console.log("got data", data);
    },
    error: function(err) {
      alert("bad request: " + err);
    }
  });

  // old fallback branch
  // return window.__cachedData;
  while (!result) {}
  return result;
}
"""


LOW_SIGNAL_PYTHON = "def add(a, b):\n    return a + b\n"


class DetectionTests(unittest.TestCase):
    def test_python_ai_like_sample_scores_as_ai(self) -> None:
        features, classification = analyze_python_code(AI_PYTHON)
        self.assertEqual(classification, "AI-Generated Code")
        self.assertGreater(features["ai_score"], features["human_score"])
        self.assertGreater(features["confidence"], 0.6)

    def test_python_human_like_sample_scores_as_human(self) -> None:
        features, classification = analyze_python_code(HUMAN_PYTHON)
        self.assertEqual(classification, "Human-Written Code")
        self.assertGreater(features["human_score"], features["ai_score"])
        self.assertIn("todo comment score", features["top_human_signals"])

    def test_javascript_ai_like_sample_scores_as_ai(self) -> None:
        features, classification = analyze_javascript_code(AI_JAVASCRIPT)
        self.assertEqual(classification, "AI-Generated Code")
        self.assertGreater(features["function_count"], 0)
        self.assertGreater(features["token_entropy"], 0.0)

    def test_javascript_human_like_sample_scores_as_human(self) -> None:
        features, classification = analyze_javascript_code(HUMAN_JAVASCRIPT)
        self.assertEqual(classification, "Human-Written Code")
        self.assertTrue(features["uses_jquery"])
        self.assertGreater(features["human_score"], features["ai_score"])

    def test_low_signal_python_sample_abstains(self) -> None:
        features, classification = analyze_python_code(LOW_SIGNAL_PYTHON)
        self.assertEqual(classification, "Uncertain (Mixed Signals)")
        self.assertEqual(features["decision_basis"], "low-signal snippet")

    def test_analyze_script_returns_detailed_metrics(self) -> None:
        process = subprocess.run(
            ["python3", str(PYTHON_DIR / "analyze.py"), "javascript", "detailed"],
            input=AI_JAVASCRIPT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(process.stdout)

        self.assertEqual(payload["language"], "javascript")
        self.assertEqual(payload["classification"], "AI-Generated Code")
        self.assertGreater(payload["features"]["function_count"], 0)
        self.assertIn("confidence", payload["features"])


if __name__ == "__main__":
    unittest.main()
