"""
LLM Manager - Handles all interactions with language models.

This module demonstrates:
- LangChain integration with multiple LLM providers
- Prompt engineering for code documentation
- Structured output parsing with Pydantic
- Error handling and fallback strategies
- Token usage tracking
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import StrOutputParser
from typing import Optional, Dict, Any, List
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.models.schemas import (
    GeneratedDocumentation,
    CodeSnippet,
    ParameterDoc,
    LanguageCode
)

logger = structlog.get_logger()


class LLMManager:
    """
    Manages interactions with Large Language Models.
    
    Supports multiple providers with automatic fallback and retry logic.
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        default_model: str = "gpt-4-turbo-preview",
        temperature: float = 0.3,
        max_tokens: int = 2000
    ):
        """Initialize LLM Manager."""
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        self.default_model = default_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize available models
        self.models = {}
        self._initialize_models()
        
        logger.info(
            "LLM Manager initialized",
            available_models=list(self.models.keys()),
            default=default_model
        )
    
    def _initialize_models(self):
        """Initialize LLM clients for available providers."""
        
        if self.openai_api_key:
            try:
                self.models["gpt-4-turbo-preview"] = ChatOpenAI(
                    api_key=self.openai_api_key,
                    model="gpt-4-turbo-preview",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                self.models["gpt-4"] = ChatOpenAI(
                    api_key=self.openai_api_key,
                    model="gpt-4",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                logger.info("OpenAI models initialized")
            except Exception as e:
                logger.warning("Failed to initialize OpenAI models", error=str(e))
        
        if self.anthropic_api_key:
            try:
                self.models["claude-3-opus"] = ChatAnthropic(
                    api_key=self.anthropic_api_key,
                    model="claude-3-opus-20240229",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                logger.info("Anthropic models initialized")
            except Exception as e:
                logger.warning("Failed to initialize Anthropic models", error=str(e))
    
    def _create_documentation_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for documentation generation."""
        
        system_template = """You are an expert technical writer and software engineer.

                Your task is to generate comprehensive documentation for code snippets.

                Guidelines:
                1. Write a clear 1-2 sentence summary
                2. Explain what the code does and why
                3. Document all parameters with types
                4. Specify return values
                5. List potential exceptions
                6. Include usage examples when helpful
                7. Mention complexity if it's an algorithm

                Output valid JSON matching this structure:

                {format_instructions}"""

        human_template = """Generate documentation for this code:

                Language: {language}
                Type: {code_type}
                File: {file_path}

                Code:
                ```{language}
                {code}
                {context}"""
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)
    
        return ChatPromptTemplate.from_messages([system_message, human_message])
    @retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
    )
    async def generate_documentation(self,snippet: CodeSnippet,model_name: Optional[str] = None,context: str = "") -> GeneratedDocumentation:
        """Generate documentation for a code snippet."""
        model_name = model_name or self.default_model
    
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not available")
    
        logger.info("Generating documentation", snippet_id=snippet.id, model=model_name)
    
        try:
            prompt = self._create_documentation_prompt()
            output_parser = PydanticOutputParser(pydantic_object=GeneratedDocumentation)
            model = self.models[model_name]
            chain = prompt | model | output_parser
        
            input_data = {
                "language": snippet.language,
                "code_type": snippet.code_type.value,
                "code": snippet.code,
                "file_path": snippet.file_path or "N/A",
                "line_start": snippet.line_start or 0,
                "line_end": snippet.line_end or 0,
                "context": context or "No additional context.",
                "format_instructions": output_parser.get_format_instructions()
            }
        
            result = await chain.ainvoke(input_data)
            result.snippet_id = snippet.id
            result.model_used = model_name
            result.confidence_score = self._calculate_confidence(result)
        
            logger.info("Documentation generated", snippet_id=snippet.id)
            return result
        
        except Exception as e:
            logger.error("Generation failed", snippet_id=snippet.id, error=str(e))
            raise

    def _calculate_confidence(self, doc: GeneratedDocumentation) -> float:
        """Calculate confidence score based on completeness."""
        score = 0.0
        if len(doc.summary) >= 20: score += 0.20
        if len(doc.detailed_description) >= 50: score += 0.20
        if doc.parameters: score += 0.15
        if doc.returns: score += 0.15
        if doc.examples: score += 0.15
        if doc.raises: score += 0.10
        if doc.complexity: score += 0.05
        return round(score, 2)

    def _create_translation_prompt(self, target_language: str) -> ChatPromptTemplate:
        """Create prompt for translation."""
        
        system_template = """You are a technical translator.
        Translate to {target_language}:

        1. Keep code snippets unchanged
        2. Keep technical terms in English
        3. Maintain formatting
        4. Be technically accurate"""
        human_template = """Translate this documentation to {target_language}:{documentation}"""
        
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)
        
        return ChatPromptTemplate.from_messages([system_message, human_message])
    
    async def translate_documentation(self,documentation: str,source_language: LanguageCode,target_language: LanguageCode,model_name: Optional[str] = None) -> str:
        """Translate documentation to another language."""
    
        model_name = model_name or list(self.models.keys())[0]
    
        logger.info("Translating", source=source_language, target=target_language)
    
        try:
            prompt = self._create_translation_prompt(target_language.value)
            model = self.models[model_name]
            chain = prompt | model | StrOutputParser()
            
            result = await chain.ainvoke({
                "target_language": target_language.value,
                "documentation": documentation
            })
        
            return result.strip()
        
        except Exception as e:
            logger.error("Translation failed", error=str(e))
            raise

    async def batch_generate(self,snippets: List[CodeSnippet],model_name: Optional[str] = None,max_concurrent: int = 5) -> List[GeneratedDocumentation]:
        """Generate documentation for multiple snippets."""
    
        import asyncio
    
        results = []
        for i in range(0, len(snippets), max_concurrent):
            batch = snippets[i:i + max_concurrent]
            batch_results = await asyncio.gather(
                *[self.generate_documentation(s, model_name) for s in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if not isinstance(result, Exception):
                    results.append(result)
            
            if i + max_concurrent < len(snippets):
                await asyncio.sleep(1)
    
        logger.info("Batch complete", total=len(snippets), successful=len(results))
        return results

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.models.keys())

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)."""
        return len(text) // 4
