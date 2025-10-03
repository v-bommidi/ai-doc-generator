"""
Mock LLM for testing without API keys.

This allows you to test the entire system without spending money on API calls.
"""

from typing import Optional, List
from src.models.schemas import (
    GeneratedDocumentation,
    CodeSnippet,
    ParameterDoc,
    LanguageCode
)
import re


class MockLLMManager:
    """
    Mock LLM that generates plausible documentation without API calls.
    
    Useful for:
    - Testing without API keys
    - Development without costs
    - Demos and presentations
    """
    
    def __init__(self, **kwargs):
        """Initialize mock LLM."""
        self.models = {
            "mock-gpt-4": "available",
            "mock-claude": "available"
        }
    
    async def generate_documentation(
        self,
        snippet: CodeSnippet,
        model_name: Optional[str] = None,
        context: str = ""
    ) -> GeneratedDocumentation:
        """Generate mock documentation based on code analysis."""
        
        # Extract function name
        function_name = self._extract_function_name(snippet.code)
        
        # Generate parameters from code
        parameters = self._extract_parameters(snippet.code)
        
        # Create plausible documentation
        doc = GeneratedDocumentation(
            snippet_id=snippet.id,
            summary=f"Implements the {function_name} operation",
            detailed_description=f"""This {snippet.code_type.value} provides functionality for {function_name}.
            
It processes the input parameters and returns the computed result. The implementation
follows standard best practices and includes error handling for edge cases.""",
            parameters=parameters,
            returns=f"Result of the {function_name} operation" if "return" in snippet.code else None,
            raises=["ValueError: If input parameters are invalid"] if "raise" in snippet.code else [],
            examples=[f"{function_name}(example_param)  # Example usage"],
            complexity="O(n)" if "for" in snippet.code or "while" in snippet.code else "O(1)",
            language=LanguageCode.ENGLISH,
            model_used=model_name or "mock-gpt-4",
            confidence_score=0.85
        )
        
        return doc
    
    def _extract_function_name(self, code: str) -> str:
        """Extract function/class name from code."""
        # Try to find function definition
        func_match = re.search(r'def\s+(\w+)', code)
        if func_match:
            return func_match.group(1)
        
        # Try to find class definition
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            return class_match.group(1)
        
        return "unknown"
    
    def _extract_parameters(self, code: str) -> List[ParameterDoc]:
        """Extract parameters from function definition."""
        # Find function signature
        func_match = re.search(r'def\s+\w+\((.*?)\):', code)
        if not func_match:
            return []
        
        params_str = func_match.group(1)
        if not params_str.strip():
            return []
        
        # Split parameters
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if not param or param == 'self':
                continue
            
            # Extract name and type hint if present
            if ':' in param:
                name, type_hint = param.split(':', 1)
                name = name.strip()
                type_hint = type_hint.split('=')[0].strip()
            else:
                name = param.split('=')[0].strip()
                type_hint = "Any"
            
            params.append(ParameterDoc(
                name=name,
                type=type_hint,
                description=f"Parameter {name} for the function",
                required='=' not in param
            ))
        
        return params
    
    async def translate_documentation(
        self,
        documentation: str,
        source_language: LanguageCode,
        target_language: LanguageCode,
        model_name: Optional[str] = None
    ) -> str:
        """Mock translation (just adds prefix)."""
        return f"[Translated to {target_language.value}]\n\n{documentation}"
    
    async def batch_generate(
        self,
        snippets: List[CodeSnippet],
        model_name: Optional[str] = None,
        max_concurrent: int = 5
    ) -> List[GeneratedDocumentation]:
        """Generate documentation for multiple snippets."""
        results = []
        for snippet in snippets:
            doc = await self.generate_documentation(snippet, model_name)
            results.append(doc)
        return results
    
    def get_available_models(self) -> List[str]:
        """Get available mock models."""
        return list(self.models.keys())
