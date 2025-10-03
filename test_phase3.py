import asyncio
from src.models.schemas import CodeSnippet, CodeType, LanguageCode
from src.core.config import get_llm_manager
from src.utils.logging import configure_logging

configure_logging(debug=True)


async def main():
    print("\n" + "="*70)
    print("PHASE 3 INTEGRATION TEST")
    print("="*70 + "\n")
    
    # Get LLM manager
    llm = get_llm_manager()
    print(f"✓ LLM Manager: {type(llm).__name__}")
    print(f"✓ Available models: {llm.get_available_models()}\n")
    
    # Test code snippets
    snippets = [
        CodeSnippet(
            id="test1",
            code="def add(a: int, b: int) -> int:\n    return a + b",
            code_type=CodeType.FUNCTION,
            file_path="math.py"
        ),
        CodeSnippet(
            id="test2",
            code="class Calculator:\n    def multiply(self, x, y):\n        return x * y",
            code_type=CodeType.CLASS,
            file_path="calc.py"
        )
    ]
    
    # Test single generation
    print("📝 Test 1: Single documentation generation")
    doc1 = await llm.generate_documentation(snippets[0])
    print(f"✓ Generated for: {doc1.snippet_id}")
    print(f"  Summary: {doc1.summary}")
    print(f"  Confidence: {doc1.confidence_score}\n")
    
    # Test batch generation
    print("📦 Test 2: Batch documentation generation")
    docs = await llm.batch_generate(snippets)
    print(f"✓ Generated {len(docs)} documents\n")
    
    # Test translation
    print("🌍 Test 3: Translation")
    translated = await llm.translate_documentation(
        doc1.summary,
        LanguageCode.ENGLISH,
        LanguageCode.SPANISH
    )
    print(f"✓ Original: {doc1.summary}")
    print(f"✓ Translated: {translated[:100]}...\n")
    
    print("="*70)
    print("✓ ALL PHASE 3 TESTS PASSED!")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())