import { SupportedLanguage } from './types';

export function detectLanguage(code: string, filename?: string): SupportedLanguage | null {
  // Check by filename extension first
  if (filename) {
    const ext = filename.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'py':
        return 'python';
      case 'js':
      case 'jsx':
      case 'ts':
      case 'tsx':
        return 'javascript';
    }
  }

  // Simple heuristic-based detection
  const pythonPatterns = [
    /^import\s+\w+/m,
    /^from\s+\w+\s+import/m,
    /^def\s+\w+\s*\(/m,
    /^class\s+\w+/m,
    /if\s+__name__\s*==\s*["']__main__["']:/,
    /^\s{4,}[^\s]/m, // Python indentation
  ];

  const jsPatterns = [
    /^const\s+\w+\s*=/m,
    /^let\s+\w+\s*=/m,
    /^var\s+\w+\s*=/m,
    /^function\s+\w+\s*\(/m,
    /^export\s+(default\s+)?/m,
    /^import\s+.*\s+from\s+["']/m,
    /=>\s*{/,
    /\{\s*\n\s*[^\s]/m, // JS/TS brace style
  ];

  const pythonScore = pythonPatterns.filter(pattern => pattern.test(code)).length;
  const jsScore = jsPatterns.filter(pattern => pattern.test(code)).length;

  if (pythonScore > jsScore) {
    return 'python';
  } else if (jsScore > pythonScore) {
    return 'javascript';
  }

  return null;
}