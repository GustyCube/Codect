# Codect: AI-Generated Code Detection
[![DeepSource](https://app.deepsource.com/gh/GustyCube/Codect.svg/?label=active+issues&show_trend=true&token=UOiRrqqUZoWYwfD_tPL8ifiy)](https://app.deepsource.com/gh/GustyCube/Codect/) <a href="LICENSE"><img src="https://img.shields.io/github/license/GustyCube/Codect" alt="License"></a>

## Overview
Codect is a free and open-source tool designed to detect whether a piece of code was written by an AI or a human. It supports multiple programming languages and provides detailed insights based on various code features such as entropy, comment ratio, AST complexity, and more.

This monorepo contains three main packages:
- **@codect/core**: Core detection algorithms and language analysis
- **@codect/cli**: Beautiful command-line interface with interactive mode
- **@codect/api**: Fast REST API server built with FastAPI

## Features
- **Multi-Language Support**: Detect AI-generated code in Python and JavaScript
- **Entropy & Complexity Analysis**: Uses token entropy and AST depth to determine AI-generated patterns
- **Comment Ratio Evaluation**: Analyzes documentation habits in code
- **Function & Loop Detection**: Evaluates structure complexity
- **Beautiful CLI**: Interactive terminal UI with colors and ASCII art
- **Fast API**: High-performance REST API with FastAPI
- **Modular Architecture**: Clean separation of concerns with monorepo structure

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=GustyCube/Codect&type=Date)](https://star-history.com/#GustyCube/Codect&Date)

## Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Git

### Setup
```bash
# Clone the repository
git clone https://github.com/GustyCube/Codect.git
cd Codect

# Install dependencies
npm install
npm run build

# Install Python dependencies for the API
cd packages/api
pip install -r requirements.txt
cd ../..
```

## Usage

### CLI Tool
The CLI provides a beautiful terminal interface for code analysis:

```bash
# Run interactive mode
npx codect

# Analyze a specific file
npx codect analyze path/to/file.py --detailed

# Get help
npx codect --help
```

Features:
- Interactive mode with menu navigation
- Beautiful ASCII art logo with gradient colors
- Colored output and progress spinners
- Detailed analysis with feature breakdown
- Support for both file and snippet analysis

### API Server
Start the API server:

```bash
cd packages/api
python main.py
```

The API will be available at `http://localhost:8000`

#### Endpoints

**Health Check**
```bash
curl http://localhost:8000/health
```

**Basic Analysis** (`/basic`)
```bash
curl -X POST "http://localhost:8000/basic" \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(x, y): return x + y", "language": "python"}'
```

**Detailed Analysis** (`/premium`)
```bash
curl -X POST "http://localhost:8000/premium" \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(x, y): return x + y", "language": "python"}'
```

### Development
```bash
# Run all packages in development mode
npm run dev

# Run tests
npm test

# Lint code
npm run lint

# Build all packages
npm run build
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
Codect is licensed under the GNU General Public v3.0 license. You are free to modify and distribute the project as needed.

## Contact
For questions or contributions, open an issue on GitHub or reach out to `gc@gustycube.xyz`.

---

Let us know if you have any suggestions! 🚀