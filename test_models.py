"""Quick test to verify Pydantic models work."""

from src.models.schemas import (
    CodeSnippet,
    CodeType,
    GeneratedDocumentation,
    LanguageCode,
    ParameterDoc,
    QualityMetrics,
    QualityEvaluation,
    DocumentationQuality
)
from datetime import datetime


def test_code_snippet():
    """Test CodeSnippet validation."""
    snippet = CodeSnippet(
        id="test123",
        code="def hello():\n    print('world')",
        code_type=CodeType.FUNCTION,
        file_path="test.py",
        line_start=1,
        line_end=2
    )
    print("✓ CodeSnippet works:", snippet.id)


def test_generated_documentation():
    """Test GeneratedDocumentation."""
    doc = GeneratedDocumentation(
        snippet_id="test123",
        summary="Prints hello world",
        detailed_description="A simple function that prints 'world' to console",
        parameters=[
            ParameterDoc(
                name="self",
                type="None",
                description="No parameters",
                required=False
            )
        ],
        model_used="gpt-4",
        confidence_score=0.95
    )
    print("✓ GeneratedDocumentation works:", doc.snippet_id)


def test_quality_evaluation():
    """Test QualityEvaluation."""
    metrics = QualityMetrics(
        accuracy_score=0.9,
        completeness_score=0.85,
        clarity_score=0.88,
        consistency_score=0.92
    )
    
    evaluation = QualityEvaluation(
        documentation_id="doc123",
        metrics=metrics,
        overall_quality=DocumentationQuality.EXCELLENT,
        evaluator_type="automated"
    )
    
    print("✓ QualityEvaluation works:", evaluation.overall_quality)
    print(f"  Overall score: {metrics.overall_score:.2f}")


if __name__ == "__main__":
    print("\nTesting Pydantic models...\n")
    test_code_snippet()
    test_generated_documentation()
    test_quality_evaluation()
    print("\n✓ All models work!\n")
