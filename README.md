# Codect: AI-Generated Code Detection

## Overview
Codect is a free and open-source tool designed to detect whether a piece of code was written by an AI or a human. It supports multiple programming languages and provides detailed insights based on various code features such as entropy, comment ratio, AST complexity, and more.

## Features
- **Multi-Language Support**: Detect AI-generated code across various programming languages.
- **Entropy & Complexity Analysis**: Uses token entropy and AST depth to determine AI-generated patterns.
- **Comment Ratio Evaluation**: Analyzes documentation habits in code.
- **Function & Loop Detection**: Evaluates structure complexity.
- **Local & Web API Support**: Can be run locally or accessed via Flask-based API.
- **Fully Open Source**: No paywalls, no restrictions—improve and contribute to the project!

## Installation
To install Codect and run it locally, follow these steps:

```bash
# Clone the repository
git clone https://github.com/GustyCube/Codect.git
cd codect

# Install dependencies
pip install -r requirements.txt

# Run the Flask API
python main.py
```

## Usage
### API Endpoints
Codect provides two main API endpoints:

#### **Basic Detection Endpoint** (`/basic`)
- Input: JSON object with `code` key.
- Output: `{ "result": 1 }` for AI-generated code, `{ "result": 0 }` for human-written code.

Example:
```bash
curl -X POST "http://localhost:5000/basic" -H "Content-Type: application/json" -d '{"code": "def add(x, y): return x + y"}'
```

#### **Premium Analysis Endpoint** (`/premium`)
- Input: JSON object with `code` key.
- Output: JSON with detailed feature extraction and classification result.

Example:
```bash
curl -X POST "http://localhost:5000/premium" -H "Content-Type: application/json" -d '{"code": "def add(x, y): return x + y"}'
```

## How It Works
1. The code is **tokenized**, and entropy is measured.
2. **Comment ratio** is calculated to analyze documentation habits.
3. **AST parsing** extracts function, loop, and exception counts.
4. The system **assigns a score** based on heuristic rules.
5. If the score exceeds a threshold, the code is flagged as **AI-generated**.

## Contributing
We welcome contributions! Feel free to:
- Submit issues & feature requests.
- Improve multi-language support.
- Optimize AI detection heuristics.
- Expand API functionality.

## License
Codect is licensed under the MIT License. You are free to modify and distribute the project as needed.

## Contact
For questions or contributions, open an issue on GitHub or reach out to `gc@gustycube.xyz`.

---

Let us know if you have any suggestions! 🚀