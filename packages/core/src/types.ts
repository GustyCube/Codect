export interface AnalysisResult {
  result: 0 | 1; // 0 = human-written, 1 = AI-generated
  classification: string;
  language: string;
  features: AnalysisFeatures;
}

export interface AnalysisFeatures {
  token_entropy: number;
  comment_ratio: number;
  function_count: number;
  loop_count: number;
  try_except_count: number;
  max_ast_depth: number;
  total_lines: number;
  [key: string]: any;
}

export type SupportedLanguage = 'python' | 'javascript';

export interface AnalyzerOptions {
  language?: SupportedLanguage;
  detailed?: boolean;
}