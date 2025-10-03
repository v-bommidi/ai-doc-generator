"""Test LLM Manager with mock implementation."""

import asyncio
from src.models.schemas import CodeSnippet, CodeType, LanguageCode
from src.core.mock_llm import MockLLMManager


async def test_mock_llm():
    """Test mock LLM manager."""
    
    # Initialize mock LLM
    llm = MockLLMManager()
    print("✓ Mock LLM initialized")
    print(f"  Available models: {llm.get_available_models()}")
    
    # Create a test code snippet
    snippet = CodeSnippet(
        id="test_factorial",
        code="""def factorial(n: int) -> int:
    '''Calculate factorial of n.'''
    if n <= 1:
        return 1
    return n * factorial(n - 1)""",
        code_type=CodeType.FUNCTION,
        file_path="math_utils.py",
        line_start=10,
        line_end=14
    )
    print(f"\n✓ Created code snippet: {snippet.id}")
    
    # Generate documentation
    print("\n📝 Generating documentation...")
    doc = await llm.generate_documentation(snippet)
    
    print(f"\n✓ Documentation generated!")
    print(f"  Model: {doc.model_used}")
    print(f"  Confidence: {doc.confidence_score}")
    print(f"  Summary: {doc.summary}")
    print(f"  Parameters: {len(doc.parameters)} found")
    for param in doc.parameters:
        print(f"    - {param.name}: {param.type}")
    print(f"  Complexity: {doc.complexity}")
    
    # Test translation
    print("\n🌍 Testing translation...")
    translated = await llm.translate_documentation(
        doc.summary,
        doc.language,
        LanguageCode.SPANISH
    )
    print(f"✓ Translation: {translated[:100]}...")
    
    # Test batch generation
    print("\n📦 Testing batch generation...")
    snippets = [snippet] * 3
    batch_docs = await llm.batch_generate(snippets)
    print(f"✓ Generated {len(batch_docs)} documents in batch")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Mock LLM Manager")
    print("="*60 + "\n")
    
    asyncio.run(test_mock_llm())
    
    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60 + "\n")
