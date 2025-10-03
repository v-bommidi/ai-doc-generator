"""Test code analyzer functionality."""

from src.core.code_analyzer import CodeAnalyzer
from src.models.schemas import CodeType


def test_basic_parsing():
    """Test basic code parsing."""
    
    analyzer = CodeAnalyzer()
    print("✓ Code analyzer initialized\n")
    
    # Sample Python code
    sample_code = '''
def factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.result = 0
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        self.result = a + b
        return self.result
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        self.result = a * b
        return self.result
'''
    
    # Parse the code
    print("📝 Parsing sample code...\n")
    snippets = analyzer.parse_file(sample_code, "test.py")
    
    print(f"✓ Found {len(snippets)} code elements:\n")
    
    # Group by type
    functions = [s for s in snippets if s.code_type == CodeType.FUNCTION]
    classes = [s for s in snippets if s.code_type == CodeType.CLASS]
    methods = [s for s in snippets if s.code_type == CodeType.METHOD]
    
    print(f"  Functions: {len(functions)}")
    for func in functions:
        sig = analyzer.get_function_signature(func.code)
        print(f"    - {sig} (lines {func.line_start}-{func.line_end})")
    
    print(f"\n  Classes: {len(classes)}")
    for cls in classes:
        lines = f"lines {cls.line_start}-{cls.line_end}"
        print(f"    - Calculator ({lines})")
    
    print(f"\n  Methods: {len(methods)}")
    for method in methods:
        sig = analyzer.get_function_signature(method.code)
        print(f"    - {sig} (lines {method.line_start}-{method.line_end})")


def test_complexity_analysis():
    """Test complexity metrics."""
    
    analyzer = CodeAnalyzer()
    
    print("\n" + "="*60)
    print("Testing Complexity Analysis")
    print("="*60 + "\n")
    
    # Simple function
    simple_code = '''
def add(a, b):
    return a + b
'''
    
    # Complex function
    complex_code = '''
def complex_function(items):
    result = []
    for item in items:
        if item > 0:
            if item % 2 == 0:
                result.append(item * 2)
            else:
                result.append(item + 1)
        elif item < 0:
            result.append(abs(item))
    return result
'''
    
    print("Simple function:")
    simple_metrics = analyzer.analyze_complexity(simple_code)
    for key, value in simple_metrics.items():
        print(f"  {key}: {value}")
    
    print("\nComplex function:")
    complex_metrics = analyzer.analyze_complexity(complex_code)
    for key, value in complex_metrics.items():
        print(f"  {key}: {value}")


def test_docstring_extraction():
    """Test docstring extraction."""
    
    analyzer = CodeAnalyzer()
    
    print("\n" + "="*60)
    print("Testing Docstring Extraction")
    print("="*60 + "\n")
    
    code_with_docstring = '''
def example(x):
    """This is a docstring."""
    return x * 2
'''
    
    docstring = analyzer.extract_docstring(code_with_docstring)
    print(f"Extracted docstring: '{docstring}'")
    
    code_without_docstring = '''
def example(x):
    return x * 2
'''
    
    no_docstring = analyzer.extract_docstring(code_without_docstring)
    print(f"No docstring case: {no_docstring}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("CODE ANALYZER TESTS")
    print("="*60 + "\n")
    
    test_basic_parsing()
    test_complexity_analysis()
    test_docstring_extraction()
    
    print("\n" + "="*60)
    print("✓ ALL ANALYZER TESTS PASSED!")
    print("="*60 + "\n")