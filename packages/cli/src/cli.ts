#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import Table from 'cli-table3';
import gradient from 'gradient-string';
import figlet from 'figlet';
import boxen from 'boxen';
import { CodeAnalyzer } from '@codect/core';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const program = new Command();
const analyzer = new CodeAnalyzer();

// Beautiful gradient for the logo
const logoGradient = gradient(['#00f260', '#0575e6']);

// ASCII art logo
function showLogo() {
  console.clear();
  const logo = figlet.textSync('CODECT', {
    font: 'ANSI Shadow',
    horizontalLayout: 'default',
    verticalLayout: 'default',
  });
  console.log(logoGradient(logo));
  console.log(
    boxen(chalk.white('AI-Generated Code Detection Tool'), {
      padding: 1,
      margin: 1,
      borderStyle: 'round',
      borderColor: 'cyan',
      align: 'center',
    })
  );
  console.log('\n');
}

// Format analysis results in a beautiful table
function displayResults(result: any, detailed: boolean = false) {
  const table = new Table({
    head: [chalk.cyan('Property'), chalk.cyan('Value')],
    style: {
      head: [],
      border: ['cyan'],
    },
    colWidths: [30, 50],
  });

  // Classification result with color
  const isAI = result.result === 1;
  const classificationColor = isAI ? chalk.red : chalk.green;
  const classificationText = isAI ? 'AI-Generated' : 'Human-Written';
  
  table.push(
    ['Classification', classificationColor.bold(classificationText)],
    ['Language', chalk.yellow(result.language)],
    ['Confidence', result.classification]
  );

  if (detailed && result.features) {
    table.push(['', '']); // Empty row for separation
    
    // Feature analysis
    const features = result.features;
    table.push(
      [chalk.dim('Token Entropy'), chalk.white(features.token_entropy?.toFixed(2) ?? 'N/A')],
      [chalk.dim('Comment Ratio'), chalk.white(features.comment_ratio != null ? (features.comment_ratio * 100).toFixed(1) + '%' : 'N/A')],
      [chalk.dim('Total Lines'), chalk.white(features.total_lines?.toString() ?? 'N/A')],
      [chalk.dim('Functions'), chalk.white(features.function_count?.toString() ?? 'N/A')],
      [chalk.dim('Loops'), chalk.white(features.loop_count?.toString() ?? 'N/A')],
      [chalk.dim('Try/Except Blocks'), chalk.white(features.try_except_count?.toString() ?? 'N/A')],
      [chalk.dim('Max AST Depth'), chalk.white(features.max_ast_depth?.toString() ?? 'N/A')]
    );
  }

  console.log(table.toString());
}

// Interactive mode
async function interactiveMode() {
  showLogo();
  
  const choices = await inquirer.prompt([
    {
      type: 'list',
      name: 'action',
      message: 'What would you like to do?',
      choices: [
        { name: '📄 Analyze a file', value: 'file' },
        { name: '✏️  Analyze code snippet', value: 'snippet' },
        { name: '❌ Exit', value: 'exit' },
      ],
    },
  ]);

  if (choices.action === 'exit') {
    console.log(chalk.yellow('\n👋 Goodbye!\n'));
    process.exit(0);
  }

  const detailed = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'detailed',
      message: 'Show detailed analysis?',
      default: false,
    },
  ]);

  if (choices.action === 'file') {
    const filePrompt = await inquirer.prompt([
      {
        type: 'input',
        name: 'filepath',
        message: 'Enter the file path:',
        validate: (input) => input.length > 0 || 'Please enter a file path',
      },
    ]);

    await analyzeFile(filePrompt.filepath, detailed.detailed);
  } else if (choices.action === 'snippet') {
    const snippetPrompt = await inquirer.prompt([
      {
        type: 'editor',
        name: 'code',
        message: 'Enter your code (press Enter to open editor):',
      },
      {
        type: 'list',
        name: 'language',
        message: 'Select the language:',
        choices: ['python', 'javascript'],
      },
    ]);

    await analyzeCode(snippetPrompt.code, snippetPrompt.language, detailed.detailed);
  }

  // Ask if user wants to continue
  const continuePrompt = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'continue',
      message: '\nWould you like to analyze more code?',
      default: true,
    },
  ]);

  if (continuePrompt.continue) {
    await interactiveMode();
  } else {
    console.log(chalk.yellow('\n👋 Goodbye!\n'));
  }
}

// Analyze file command
async function analyzeFile(filepath: string, detailed: boolean = false) {
  const spinner = ora('Analyzing code...').start();
  
  try {
    const fullPath = resolve(filepath);
    const result = await analyzer.analyzeFile(fullPath, { detailed });
    
    spinner.succeed('Analysis complete!');
    console.log('\n');
    displayResults(result, detailed);
  } catch (error: any) {
    spinner.fail('Analysis failed!');
    console.error(chalk.red(`\nError: ${error.message}\n`));
  }
}

// Analyze code snippet
async function analyzeCode(code: string, language: string, detailed: boolean = false) {
  const spinner = ora('Analyzing code...').start();
  
  try {
    const result = await analyzer.analyze(code, { 
      language: language as any, 
      detailed 
    });
    
    spinner.succeed('Analysis complete!');
    console.log('\n');
    displayResults(result, detailed);
  } catch (error: any) {
    spinner.fail('Analysis failed!');
    console.error(chalk.red(`\nError: ${error.message}\n`));
  }
}

// CLI setup
program
  .name('codect')
  .description('AI-Generated Code Detection CLI')
  .version('1.0.0');

program
  .command('analyze <file>')
  .description('Analyze a code file')
  .option('-d, --detailed', 'Show detailed analysis', false)
  .option('-l, --language <language>', 'Specify language (python/javascript)')
  .action(async (file, options) => {
    showLogo();
    await analyzeFile(file, options.detailed);
  });

program
  .command('snippet <code>')
  .alias('s')
  .description('Analyze a code snippet directly')
  .option('-d, --detailed', 'Show detailed analysis', false)
  .option('-l, --language <language>', 'Specify language (python/javascript)', 'python')
  .action(async (code, options) => {
    showLogo();
    await analyzeCode(code, options.language, options.detailed);
  });

program
  .command('stdin')
  .description('Analyze code from stdin')
  .option('-d, --detailed', 'Show detailed analysis', false)
  .option('-l, --language <language>', 'Specify language (python/javascript)', 'python')
  .action(async (options) => {
    showLogo();
    
    // Read from stdin
    let code = '';
    process.stdin.setEncoding('utf8');
    
    process.stdin.on('data', (chunk) => {
      code += chunk;
    });
    
    process.stdin.on('end', async () => {
      await analyzeCode(code, options.language, options.detailed);
    });
  });

program
  .command('interactive')
  .alias('i')
  .description('Start interactive mode')
  .action(async () => {
    await interactiveMode();
  });

// Default to interactive mode if no command is provided
if (process.argv.length === 2) {
  interactiveMode();
} else {
  program.parse(process.argv);
}