"""Utilities for processing multiple files."""

import os
from pathlib import Path
from typing import List, Dict, Any
import structlog

from src.core.code_analyzer import CodeAnalyzer
from src.models.schemas import CodeSnippet

logger = structlog.get_logger()


class FileProcessor:
    """Process multiple Python files for documentation."""
    
    def __init__(self):
        """Initialize file processor."""
        self.analyzer = CodeAnalyzer()
    
    def process_directory(
        self,
        directory: str,
        recursive: bool = True,
        exclude_patterns: List[str] = None
    ) -> Dict[str, List[CodeSnippet]]:
        """
        Process all Python files in a directory.
        
        Args:
            directory: Directory path
            recursive: Whether to search recursively
            exclude_patterns: Patterns to exclude (e.g., ['test_', '__pycache__'])
            
        Returns:
            Dictionary mapping file paths to code snippets
        """
        
        exclude_patterns = exclude_patterns or ['test_', '__pycache__', '.git', 'venv']
        
        results = {}
        python_files = self._find_python_files(directory, recursive, exclude_patterns)
        
        logger.info(
            "Processing directory",
            directory=directory,
            files_found=len(python_files)
        )
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                snippets = self.analyzer.parse_file(content, file_path)
                results[file_path] = snippets
                
                logger.debug(
                    "Processed file",
                    file=file_path,
                    snippets=len(snippets)
                )
                
            except Exception as e:
                logger.error(
                    "Failed to process file",
                    file=file_path,
                    error=str(e)
                )
        
        return results
    
    def _find_python_files(
        self,
        directory: str,
        recursive: bool,
        exclude_patterns: List[str]
    ) -> List[str]:
        """Find all Python files in directory."""
        
        python_files = []
        path = Path(directory)
        
        pattern = "**/*.py" if recursive else "*.py"
        
        for file_path in path.glob(pattern):
            # Check if file should be excluded
            if any(pattern in str(file_path) for pattern in exclude_patterns):
                continue
            
            python_files.append(str(file_path))
        
        return sorted(python_files)
    
    def get_statistics(self, results: Dict[str, List[CodeSnippet]]) -> Dict[str, Any]:
        """Get statistics about processed files."""
        
        total_files = len(results)
        total_snippets = sum(len(snippets) for snippets in results.values())
        
        from src.models.schemas import CodeType
        functions = sum(
            len([s for s in snippets if s.code_type == CodeType.FUNCTION])
            for snippets in results.values()
        )
        classes = sum(
            len([s for s in snippets if s.code_type == CodeType.CLASS])
            for snippets in results.values()
        )
        methods = sum(
            len([s for s in snippets if s.code_type == CodeType.METHOD])
            for snippets in results.values()
        )
        
        return {
            "total_files": total_files,
            "total_snippets": total_snippets,
            "functions": functions,
            "classes": classes,
            "methods": methods
        }