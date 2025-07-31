#!/usr/bin/env python3
"""
Test script for code analyzers
"""
import sys
sys.path.append('./python')

from python_analyzer import analyze_python_code
from javascript_analyzer import analyze_javascript_code

# Test Python code samples
ai_python_code = '''
def calculate_area(radius):
    """Calculate the area of a circle given its radius."""
    import math
    return math.pi * radius ** 2

def calculate_perimeter(radius):
    """Calculate the perimeter of a circle given its radius."""
    import math
    return 2 * math.pi * radius

def main():
    radius = 5
    area = calculate_area(radius)
    perimeter = calculate_perimeter(radius)
    print(f"Area: {area}")
    print(f"Perimeter: {perimeter}")

if __name__ == "__main__":
    main()
'''

human_python_code = '''
import os
import sys

# TODO: refactor this mess
def process_data(input_file):
    # quick hack to fix encoding issues
    data = []
    
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
    except:
        print("debug: file not found")  # remove this later
        return None
        
    for line in lines:
        # commented out old processing
        # if line.startswith('#'):
        #     continue
        
        tmp = line.strip()
        if tmp:  # check if not empty
            data.append(tmp)
            
    # magic number alert!
    if len(data) > 42:
        print("Warning: too much data!")
        
    return data

# FIXME: This is a temporary solution
result = process_data('test.txt')
'''

# Test JavaScript code samples
ai_js_code = '''
function fibonacci(n) {
  if (n <= 1) {
    return n;
  }
  return fibonacci(n - 1) + fibonacci(n - 2);
}

function factorial(n) {
  if (n === 0 || n === 1) {
    return 1;
  }
  return n * factorial(n - 1);
}

// Example usage
const num = 10;
console.log(`Fibonacci of ${num} is ${fibonacci(num)}`);
console.log(`Factorial of ${num} is ${factorial(num)}`);
'''

human_js_code = '''
var config = require('./config');
const $ = require('jquery');

// TODO: clean up this code
function getData() {
    var result;
    
    console.log('fetching data...');  // debug
    
    $.ajax({
        url: '/api/data',
        success: function(data) {
            // handle response
            result = data;
            console.log("got data:", data);
        },
        error: function(err) {
            alert('Error: ' + err);  // fix this later
        }
    });
    
    // HACK: wait for ajax to complete
    while (!result) {
        // busy wait
    }
    
    return result;
}

// old function, keeping for reference
// function oldGetData() {
//     return fetch('/api/data');
// }

module.exports = {
    getData: getData
};
'''

def test_analyzers():
    print("Testing Code Analyzers\n")
    print("=" * 60)
    
    # Test Python analyzer
    print("\n1. AI-Generated Python Code:")
    features, classification = analyze_python_code(ai_python_code)
    confidence = features.get('confidence', 0)
    print(f"Classification: {classification}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Key features: {', '.join(k for k, v in features.items() if v and isinstance(v, bool))}")
    
    print("\n2. Human-Written Python Code:")
    features, classification = analyze_python_code(human_python_code)
    confidence = features.get('confidence', 0)
    print(f"Classification: {classification}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Key features: {', '.join(k for k, v in features.items() if v and isinstance(v, bool))}")
    
    print("\n" + "=" * 60)
    
    # Test JavaScript analyzer
    print("\n3. AI-Generated JavaScript Code:")
    features, classification = analyze_javascript_code(ai_js_code)
    confidence = features.get('confidence', 0)
    print(f"Classification: {classification}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Key features: {', '.join(k for k, v in features.items() if v and isinstance(v, bool))}")
    
    print("\n4. Human-Written JavaScript Code:")
    features, classification = analyze_javascript_code(human_js_code)
    confidence = features.get('confidence', 0)
    print(f"Classification: {classification}")
    print(f"Confidence: {confidence:.2%}")
    print(f"Key features: {', '.join(k for k, v in features.items() if v and isinstance(v, bool))}")

if __name__ == "__main__":
    test_analyzers()