"""Test complete workflow: Parse code → Generate docs."""

import asyncio
from src.core.code_analyzer import CodeAnalyzer
from src.core.mock_llm import MockLLMManager


async def test_complete_workflow():
    """Test the complete documentation generation workflow."""
    
    print("\n" + "="*70)
    print("COMPLETE WORKFLOW TEST: Code Analysis → Documentation")
    print("="*70 + "\n")
    
    # Initialize components
    analyzer = CodeAnalyzer()
    llm = MockLLMManager()
    
    print("✓ Components initialized\n")
    
    # Sample code to document
    sample_code = '''
def bubble_sort(arr: list) -> list:
    """Sort array using bubble sort algorithm."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

class DataProcessor:
    """Process and transform data."""
    
    def __init__(self, data):
        self.data = data
    
    def filter_positive(self):
        """Filter out negative values."""
        return [x for x in self.data if x > 0]
    
    def normalize(self):
        """Normalize data to 0-1 range."""
        min_val = min(self.data)
        max_val = max(self.data)
        return [(x - min_val) / (max_val - min_val) for x in self.data]
'''
    
    # Step 1: Parse code
    print("Step 1: Parsing code...")
    snippets = analyzer.parse_file(sample_code, "data_utils.py")
    print(f"✓ Extracted {len(snippets)} code elements\n")
    
    # Step 2: Analyze complexity
    print("Step 2: Analyzing complexity...")
    for snippet in snippets:
        metrics = analyzer.analyze_complexity(snippet.code)
        print(f"  {snippet.code_type.value}: complexity={metrics['cyclomatic_complexity']}, rating={metrics['complexity_rating']}")
    print()
    
    # Step 3: Generate documentation
    print("Step 3: Generating documentation...\n")
    docs = []
    for snippet in snippets[:2]:  # Just do first 2 for demo
        doc = await llm.generate_documentation(snippet)
        docs.append(doc)
        
        sig = analyzer.get_function_signature(snippet.code) or snippet.code_type.value
        print(f"✓ {sig}")
        print(f"  Summary: {doc.summary}")
        print(f"  Confidence: {doc.confidence_score}")
        print()
    
    # Step 4: Show statistics
    print("="*70)
    print("WORKFLOW COMPLETE!")
    print("="*70)
    print(f"\nStatistics:")
    print(f"  Code elements analyzed: {len(snippets)}")
    print(f"  Documentation generated: {len(docs)}")
    print(f"  Average confidence: {sum(d.confidence_score for d in docs) / len(docs):.2f}")
    print()


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())