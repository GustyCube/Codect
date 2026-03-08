# Codect: AI-Generated Code Detection
[![DeepSource](https://app.deepsource.com/gh/GustyCube/Codect.svg/?label=active+issues&show_trend=true&token=UOiRrqqUZoWYwfD_tPL8ifiy)](https://app.deepsource.com/gh/GustyCube/Codect/) <a href="LICENSE"><img src="https://img.shields.io/github/license/GustyCube/Codect" alt="License"></a>

## Overview
Codect is a free and open-source tool designed to detect whether a piece of code was written by an AI or a human. It currently supports Python and JavaScript, and reports both a classification and supporting heuristics such as token entropy, comment density, structural complexity, and signal strength.

This monorepo contains three main packages:
- **@codect/core**: Core detection algorithms and language analysis
- **@codect/cli**: Beautiful command-line interface with interactive mode
- **@codect/api**: Fast REST API server built with FastAPI

## Features
- **Multi-Language Support**: Detect AI-generated code in Python and JavaScript
- **Chunk-Level Detection**: Splits longer files into chunks and aggregates their results instead of relying on a single whole-file score
- **Low-Signal Abstention**: Returns `Uncertain (Mixed Signals)` for snippets that do not contain enough evidence
- **Entropy & Complexity Analysis**: Uses token entropy, nesting depth, naming patterns, and formatting consistency as part of the score
- **Human vs AI Signals**: Tracks both AI-like and human-like indicators such as example-heavy code, TODO comments, debug statements, and repeated structure
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
- Detailed analysis with feature breakdown and confidence
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
1. The code is split into **chunks** so larger files can be evaluated on local signal instead of one global pass.
2. Each chunk is **tokenized** and measured for entropy, comment ratio, naming patterns, formatting consistency, and structural complexity.
3. Language-specific analyzers extract **Python AST metrics** or **JavaScript structural metrics** such as function count, loop count, try/catch usage, and nesting depth.
4. The detector computes both **AI-oriented** and **human-oriented** heuristic scores for each chunk.
5. Results are **aggregated across chunks** into a final classification, confidence score, and supporting signals.
6. If the snippet is too short or the heuristics conflict, the detector abstains with **`Uncertain (Mixed Signals)`**.

## Testing
The repository now includes regression tests for the detector in [`packages/core/tests`](./packages/core/tests). The current suite covers:
- AI-like and human-like Python samples
- AI-like and human-like JavaScript samples
- Low-signal abstention behavior
- End-to-end validation of the Python analysis bridge used by the TypeScript wrapper

Run the full workspace tests with:

```bash
npm test
```

Or run the detector regression suite directly with:

```bash
python3 -m unittest discover -s packages/core/tests -p 'test_*.py'
```

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
