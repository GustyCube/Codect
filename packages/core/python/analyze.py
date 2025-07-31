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

        # Map Python analyzer features to expected TypeScript interface
        mapped_features = {
            "token_entropy": features.get("token_entropy", 0),
            "comment_ratio": features.get("comment_ratio", 0),
            "total_lines": len(code.splitlines()),
            "function_count": features.get("function_count", 0),
            "loop_count": features.get("loop_count", 0),
            "try_except_count": features.get("try_except_count", 0),
            "max_ast_depth": features.get("max_ast_depth", 0)
        }
        
        if mode == 'basic':
            response = {
                "result": result,
                "classification": classification,
                "language": language,
                "features": {
                    "token_entropy": mapped_features["token_entropy"],
                    "comment_ratio": mapped_features["comment_ratio"],
                    "total_lines": mapped_features["total_lines"]
                }
            }
        else:  # detailed
            # Include all mapped features plus additional ones for detailed mode
            detailed_features = mapped_features.copy()
            detailed_features.update(features)  # Add all other features
            
            response = {
                "result": result,
                "classification": classification,
                "language": language,
                "features": detailed_features
            }

        print(json.dumps(response))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()
