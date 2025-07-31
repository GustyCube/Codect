import { PythonShell } from 'python-shell';
import * as path from 'path';
import { AnalysisResult, AnalyzerOptions, SupportedLanguage } from './types';
import { detectLanguage } from './language-detector';

export class CodeAnalyzer {
  private pythonPath: string;

  constructor() {
    this.pythonPath = path.join(__dirname, '..', 'python');
  }

  async analyze(code: string, options: AnalyzerOptions = {}): Promise<AnalysisResult> {
    const language = options.language || detectLanguage(code);
    
    if (!language) {
      throw new Error('Unable to detect language. Please specify the language explicitly.');
    }

    if (language !== 'python' && language !== 'javascript') {
      throw new Error(`Unsupported language: ${language}`);
    }

    const scriptPath = path.join(this.pythonPath, 'analyze.py');
    
    const pyOptions = {
      mode: 'json' as const,
      pythonPath: 'python3',
      pythonOptions: ['-u'],
      scriptPath: this.pythonPath,
      args: [language, options.detailed ? 'detailed' : 'basic']
    };

    return new Promise((resolve, reject) => {
      const pyshell = new PythonShell(scriptPath, pyOptions);
      
      pyshell.send(code);
      
      pyshell.on('message', (message: any) => {
        resolve(message as AnalysisResult);
      });
      
      pyshell.on('error', (err) => {
        reject(err);
      });
      
      pyshell.end((err) => {
        if (err) reject(err);
      });
    });
  }

  async analyzeFile(filePath: string, options: AnalyzerOptions = {}): Promise<AnalysisResult> {
    const fs = await import('fs/promises');
    const code = await fs.readFile(filePath, 'utf-8');
    const detectedLanguage = options.language || detectLanguage(code, filePath) || undefined;
    
    return this.analyze(code, { ...options, language: detectedLanguage });
  }
}