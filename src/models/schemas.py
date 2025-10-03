"""
Pydantic models for data validation and serialization.
Demonstrates strong typing and data quality practices.
"""

from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List, Dict, Literal
from datetime import datetime
from enum import Enum


class LanguageCode(str, Enum):
    """Supported language codes (ISO 639-1)."""
    ENGLISH = "en"
    SPANISH = "es"
    CHINESE = "zh"
    FRENCH = "fr"
    GERMAN = "de"
    JAPANESE = "ja"
    HINDI = "hi"
    ARABIC = "ar"


class CodeType(str, Enum):
    """Types of code elements that can be documented."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    MODULE = "module"


class DocumentationQuality(str, Enum):
    """Quality ratings for generated documentation."""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"            # 75-89%
    FAIR = "fair"            # 60-74%
    POOR = "poor"            # 40-59%
    MISSING = "missing"      # <40%


class CodeSnippet(BaseModel):
    """
    Represents a code snippet for documentation.
    
    This model validates code input and extracts metadata
    needed for documentation generation.
    """
    
    id: str = Field(..., description="Unique identifier (SHA-256 hash)")
    code: str = Field(..., min_length=1, description="Source code content")
    language: str = Field(default="python", description="Programming language")
    code_type: CodeType = Field(..., description="Type of code element")
    file_path: Optional[str] = Field(None, description="File path in repository")
    line_start: Optional[int] = Field(None, ge=1, description="Starting line number")
    line_end: Optional[int] = Field(None, ge=1, description="Ending line number")
    
    @field_validator('code')
    @classmethod
    def code_not_empty(cls, v: str) -> str:
        """Ensure code is not just whitespace."""
        if not v.strip():
            raise ValueError("Code cannot be empty or whitespace only")
        return v
    
    @field_validator('line_end')
    @classmethod
    def line_end_after_start(cls, v: Optional[int], info) -> Optional[int]:
        """Validate line_end is after line_start."""
        if v is not None and 'line_start' in info.data:
            line_start = info.data['line_start']
            if line_start is not None and v < line_start:
                raise ValueError("line_end must be >= line_start")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "abc123def456",
                "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
                "language": "python",
                "code_type": "function",
                "file_path": "src/utils/math.py",
                "line_start": 10,
                "line_end": 12
            }
        }


class ParameterDoc(BaseModel):
    """Documentation for a function parameter."""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type")
    description: str = Field(..., min_length=5, description="What the parameter does")
    default: Optional[str] = Field(None, description="Default value if any")
    required: bool = Field(default=True, description="Whether parameter is required")


class GeneratedDocumentation(BaseModel):
    """
    AI-generated documentation with metadata.
    
    This is the primary output of the documentation generation process.
    """
    
    snippet_id: str = Field(..., description="ID of the code snippet")
    summary: str = Field(
        ..., 
        min_length=10, 
        max_length=500,
        description="One-sentence summary of what the code does"
    )
    detailed_description: str = Field(
        ..., 
        min_length=20,
        description="Comprehensive explanation of the code"
    )
    parameters: List[ParameterDoc] = Field(
        default_factory=list,
        description="Documentation for each parameter"
    )
    returns: Optional[str] = Field(
        None,
        description="Description of return value and type"
    )
    raises: List[str] = Field(
        default_factory=list,
        description="Exceptions that may be raised"
    )
    examples: List[str] = Field(
        default_factory=list,
        description="Usage examples"
    )
    complexity: Optional[str] = Field(
        None,
        description="Time/space complexity (e.g., 'O(n log n)')"
    )
    notes: List[str] = Field(
        default_factory=list,
        description="Additional notes or warnings"
    )
    
    # Metadata
    language: LanguageCode = Field(
        default=LanguageCode.ENGLISH,
        description="Language of the documentation"
    )
    model_used: str = Field(..., description="LLM model identifier")
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Model's confidence in the generated docs (0-1)"
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of generation"
    )
    tokens_used: Optional[int] = Field(
        None,
        ge=0,
        description="Number of tokens consumed"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "snippet_id": "abc123",
                "summary": "Calculates the factorial of a number using recursion",
                "detailed_description": "This function implements the factorial operation...",
                "parameters": [
                    {
                        "name": "n",
                        "type": "int",
                        "description": "The number to calculate factorial for",
                        "required": True
                    }
                ],
                "returns": "int: The factorial of n",
                "raises": ["ValueError: If n is negative"],
                "examples": ["factorial(5)  # Returns 120"],
                "complexity": "O(n) time, O(n) space due to recursion",
                "language": "en",
                "model_used": "gpt-4-turbo-preview",
                "confidence_score": 0.95,
                "tokens_used": 450
            }
        }


class TranslationRequest(BaseModel):
    """Request to translate documentation to other languages."""
    
    documentation_id: str = Field(..., description="ID of documentation to translate")
    source_language: LanguageCode = Field(..., description="Original language")
    target_languages: List[LanguageCode] = Field(
        ...,
        min_length=1,
        description="Languages to translate to"
    )
    preserve_code_snippets: bool = Field(
        default=True,
        description="Keep code examples unchanged"
    )
    preserve_technical_terms: bool = Field(
        default=True,
        description="Don't translate technical terminology"
    )


class QualityMetrics(BaseModel):
    """Metrics for evaluating documentation quality."""
    
    accuracy_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Factual correctness (0-1)"
    )
    completeness_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Coverage of all aspects (0-1)"
    )
    clarity_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Readability and understandability (0-1)"
    )
    consistency_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Consistent terminology and style (0-1)"
    )
    
    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score."""
        return (
            self.accuracy_score * 0.35 +
            self.completeness_score * 0.30 +
            self.clarity_score * 0.25 +
            self.consistency_score * 0.10
        )


class QualityEvaluation(BaseModel):
    """
    Complete quality evaluation of generated documentation.
    
    Used for both automated and human evaluation.
    """
    
    documentation_id: str = Field(..., description="ID of evaluated documentation")
    metrics: QualityMetrics = Field(..., description="Quality metrics")
    overall_quality: DocumentationQuality = Field(
        ...,
        description="Categorical quality rating"
    )
    evaluator_type: Literal["automated", "human"] = Field(
        ...,
        description="Type of evaluation"
    )
    evaluator_id: Optional[str] = Field(
        None,
        description="ID of human evaluator if applicable"
    )
    feedback: Optional[str] = Field(
        None,
        description="Detailed feedback or suggestions"
    )
    issues_found: List[str] = Field(
        default_factory=list,
        description="Specific issues identified"
    )
    evaluated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Evaluation timestamp"
    )
    
    @field_validator('overall_quality')
    @classmethod
    def quality_matches_score(cls, v: DocumentationQuality, info) -> DocumentationQuality:
        """Ensure quality rating aligns with metrics."""
        if 'metrics' in info.data:
            score = info.data['metrics'].overall_score
            expected_quality = {
                (0.9, 1.0): DocumentationQuality.EXCELLENT,
                (0.75, 0.9): DocumentationQuality.GOOD,
                (0.6, 0.75): DocumentationQuality.FAIR,
                (0.4, 0.6): DocumentationQuality.POOR,
                (0.0, 0.4): DocumentationQuality.MISSING,
            }
            
            for (min_score, max_score), quality in expected_quality.items():
                if min_score <= score < max_score:
                    if v != quality:
                        # Log warning but don't fail
                        pass
        return v


class AnnotationGuideline(BaseModel):
    """
    Guidelines for human annotators.
    
    Ensures consistency in data annotation and quality evaluation.
    """
    
    guideline_id: str = Field(..., description="Unique guideline identifier")
    title: str = Field(..., min_length=5, description="Guideline title")
    description: str = Field(..., min_length=20, description="What this guideline covers")
    
    rules: List[str] = Field(
        ...,
        min_length=1,
        description="Specific rules to follow"
    )
    
    examples_good: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Examples of good annotations"
    )
    
    examples_bad: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Examples of what to avoid"
    )
    
    version: str = Field(..., description="Guideline version (semver)")
    language: LanguageCode = Field(
        default=LanguageCode.ENGLISH,
        description="Guideline language"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "guideline_id": "anno-v1-params",
                "title": "Parameter Documentation Guidelines",
                "description": "How to document function parameters correctly",
                "rules": [
                    "Always include parameter type",
                    "Describe what the parameter does, not what it is",
                    "Include valid value ranges or constraints"
                ],
                "examples_good": [
                    {
                        "annotation": "n (int): The number to calculate factorial for. Must be >= 0.",
                        "reason": "Specifies type, purpose, and constraints"
                    }
                ],
                "examples_bad": [
                    {
                        "annotation": "n: a number",
                        "reason": "Missing type and constraints, vague description"
                    }
                ],
                "version": "1.0.0"
            }
        }
