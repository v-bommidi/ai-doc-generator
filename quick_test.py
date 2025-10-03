print("Testing imports...")

try:
    from src.models.schemas import CodeSnippet, CodeType, LanguageCode
    print("✓ Models imported")
except Exception as e:
    print(f"✗ Models import failed: {e}")
    exit(1)

try:
    from src.core.mock_llm import MockLLMManager
    print("✓ Mock LLM imported")
except Exception as e:
    print(f"✗ Mock LLM import failed: {e}")
    exit(1)

try:
    import asyncio
    print("✓ asyncio imported")
except Exception as e:
    print(f"✗ asyncio import failed: {e}")
    exit(1)

print("\n✓ All imports successful!")
print("\nNow testing basic functionality...\n")

# Test creating a code snippet
snippet = CodeSnippet(
    id="test1",
    code="def hello(): pass",
    code_type=CodeType.FUNCTION
)
print(f"✓ Created snippet: {snippet.id}")

# Test creating mock LLM
llm = MockLLMManager()
print(f"✓ Created mock LLM")
print(f"  Models: {llm.get_available_models()}")

print("\n✓ Everything works!")