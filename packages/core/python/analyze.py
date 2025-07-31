#!/usr/bin/env python3
import sys
import json
from python_analyzer import analyze_python_code
from javascript_analyzer import analyze_javascript_code

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing arguments"}))
        sys.exit(1)

    language = sys.argv[1]
    mode = sys.argv[2]  # 'basic' or 'detailed'

    # Read code from stdin
    code = sys.stdin.read()

    try:
        if language == 'python':
            features, classification = analyze_python_code(code)
        elif language == 'javascript':
            features, classification = analyze_javascript_code(code)
        else:
            print(json.dumps({"error": f"Unsupported language: {language}"}))
            sys.exit(1)

        result = 1 if classification == "AI-Generated Code" else 0

        if mode == 'basic':
            response = {
                "result": result,
                "classification": classification,
                "language": language,
                "features": {
                    "token_entropy": features.get("token_entropy", 0),
                    "comment_ratio": features.get("comment_ratio", 0),
                    "total_lines": features.get("total_lines", 0)
                }
            }
        else:  # detailed
            response = {
                "result": result,
                "classification": classification,
                "language": language,
                "features": features
            }

        print(json.dumps(response))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()
