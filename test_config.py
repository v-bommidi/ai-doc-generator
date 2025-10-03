"""Test configuration loading."""

from src.core.config import settings, get_llm_manager


def test_config():
    """Test configuration."""
    print("\n📋 Configuration Settings:")
    print(f"  Debug mode: {settings.debug}")
    print(f"  API Host: {settings.api_host}")
    print(f"  API Port: {settings.api_port}")
    print(f"  Default model: {settings.default_model}")
    print(f"  Temperature: {settings.llm_temperature}")
    print(f"  Database URL: {settings.database_url}")
    print(f"  Redis URL: {settings.redis_url}")
    
    # Check API keys
    has_openai = "✓" if settings.openai_api_key else "✗"
    has_anthropic = "✓" if settings.anthropic_api_key else "✗"
    
    print(f"\n🔑 API Keys:")
    print(f"  OpenAI: {has_openai}")
    print(f"  Anthropic: {has_anthropic}")
    
    # Get LLM manager
    print(f"\n🤖 LLM Manager:")
    llm = get_llm_manager()
    print(f"  Type: {type(llm).__name__}")
    print(f"  Available models: {llm.get_available_models()}")
    
    if "Mock" in type(llm).__name__:
        print("\n⚠️  Using Mock LLM (no API keys configured)")
        print("   Add API keys to .env to use real LLMs")
    else:
        print("\n✓ Using real LLM with API keys")


if __name__ == "__main__":
    test_config()
    print("\n✓ Configuration loaded successfully!\n")
