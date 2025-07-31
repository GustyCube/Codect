import * as path from 'path';
import { spawn } from 'child_process';
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
    
    // Use spawn instead of PythonShell for better control
    return new Promise((resolve, reject) => {
      const args = [scriptPath, language, options.detailed ? 'detailed' : 'basic'];
      const pythonProcess = spawn('python3', args);
      
      let stdout = '';
      let stderr = '';
      
      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });
      
      pythonProcess.on('close', (exitCode) => {
        if (exitCode !== 0) {
          reject(new Error(`Python process exited with code ${exitCode}: ${stderr}`));
          return;
        }
        
        try {
          const result = JSON.parse(stdout);
          resolve(result as AnalysisResult);
        } catch (err) {
          reject(new Error(`Failed to parse Python output: ${stdout}`));
        }
      });
      
      pythonProcess.on('error', (err) => {
        reject(err);
      });
      
      // Write code to stdin and close
      pythonProcess.stdin.write(code);
      pythonProcess.stdin.end();
    });
  }

  async analyzeFile(filePath: string, options: AnalyzerOptions = {}): Promise<AnalysisResult> {
    const fs = await import('fs/promises');
    const code = await fs.readFile(filePath, 'utf-8');
    const detectedLanguage = options.language || detectLanguage(code, filePath) || undefined;
    
    return this.analyze(code, { ...options, language: detectedLanguage });
  }
}