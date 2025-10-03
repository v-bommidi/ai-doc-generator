"""
Code Analyzer - Extracts documentable elements from source code.

Uses tree-sitter 0.23+ API.
"""

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node
from typing import List, Optional, Dict, Any
import hashlib

from src.models.schemas import CodeSnippet, CodeType
import structlog

logger = structlog.get_logger()


class CodeAnalyzer:
    """Analyzes source code and extracts documentable elements."""
    
    def __init__(self):
        """Initialize the code analyzer with Python support."""
        # Initialize tree-sitter for Python (new API)
        self.parser = Parser(Language(tspython.language()))
        
        logger.info("Code analyzer initialized", language="python")
    
    def parse_file(self, file_content: str, file_path: str = "unknown.py") -> List[CodeSnippet]:
        """Parse a Python file and extract all documentable elements."""
        
        try:
            tree = self.parser.parse(bytes(file_content, "utf8"))
            snippets = []
            
            # Extract functions (top-level)
            snippets.extend(self._extract_functions(
                tree.root_node, 
                file_content, 
                file_path,
                is_method=False
            ))
            
            # Extract classes and their methods
            snippets.extend(self._extract_classes(
                tree.root_node,
                file_content,
                file_path
            ))
            
            logger.info(
                "File parsed successfully",
                file=file_path,
                functions=len([s for s in snippets if s.code_type == CodeType.FUNCTION]),
                classes=len([s for s in snippets if s.code_type == CodeType.CLASS]),
                methods=len([s for s in snippets if s.code_type == CodeType.METHOD])
            )
            
            return snippets
            
        except Exception as e:
            logger.error("Failed to parse file", file=file_path, error=str(e))
            raise
    
    def _extract_functions(
        self,
        node: Node,
        source_code: str,
        file_path: str,
        is_method: bool = False
    ) -> List[CodeSnippet]:
        """Extract function definitions from AST."""
        snippets = []
        
        if node.type == "function_definition":
            # Get function name
            name_node = node.child_by_field_name("name")
            function_name = self._get_node_text(name_node, source_code) if name_node else "unknown"
            
            # Skip private/dunder methods unless they're __init__
            if is_method and function_name.startswith("_") and function_name != "__init__":
                logger.debug("Skipping private method", name=function_name)
            else:
                code = self._get_node_text(node, source_code)
                snippet_id = self._generate_id(code, file_path)
                
                snippet = CodeSnippet(
                    id=snippet_id,
                    code=code,
                    language="python",
                    code_type=CodeType.METHOD if is_method else CodeType.FUNCTION,
                    file_path=file_path,
                    line_start=node.start_point[0] + 1,
                    line_end=node.end_point[0] + 1,
                )
                snippets.append(snippet)
                
                logger.debug(
                    "Extracted function",
                    name=function_name,
                    type="method" if is_method else "function",
                    lines=f"{snippet.line_start}-{snippet.line_end}"
                )
        
        # Recursively search children
        if node.type != "function_definition":
            for child in node.children:
                snippets.extend(self._extract_functions(
                    child, 
                    source_code, 
                    file_path,
                    is_method
                ))
        
        return snippets
    
    def _extract_classes(
        self,
        node: Node,
        source_code: str,
        file_path: str
    ) -> List[CodeSnippet]:
        """Extract class definitions and their methods."""
        snippets = []
        
        if node.type == "class_definition":
            # Get class name
            name_node = node.child_by_field_name("name")
            class_name = self._get_node_text(name_node, source_code) if name_node else "unknown"
            
            # Extract the class itself
            code = self._get_node_text(node, source_code)
            snippet_id = self._generate_id(code, file_path)
            
            snippet = CodeSnippet(
                id=snippet_id,
                code=code,
                language="python",
                code_type=CodeType.CLASS,
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
            )
            snippets.append(snippet)
            
            logger.debug(
                "Extracted class",
                name=class_name,
                lines=f"{snippet.line_start}-{snippet.line_end}"
            )
            
            # Extract methods within the class
            body_node = node.child_by_field_name("body")
            if body_node:
                for child in body_node.children:
                    if child.type == "function_definition":
                        method_snippets = self._extract_functions(
                            child,
                            source_code,
                            file_path,
                            is_method=True
                        )
                        snippets.extend(method_snippets)
        
        # Recursively search children
        for child in node.children:
            if child.type != "class_definition":
                snippets.extend(self._extract_classes(child, source_code, file_path))
        
        return snippets
    
    def _get_node_text(self, node: Node, source_code: str) -> str:
        """Extract source code text from a tree-sitter node."""
        return source_code[node.start_byte:node.end_byte]
    
    def _generate_id(self, code: str, file_path: str) -> str:
        """Generate unique ID for a code snippet."""
        content = f"{file_path}:{code}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def analyze_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze code complexity metrics."""
        
        tree = self.parser.parse(bytes(code, "utf8"))
        
        metrics = {
            "lines": code.count('\n') + 1,
            "cyclomatic_complexity": self._calculate_cyclomatic_complexity(tree.root_node),
            "nesting_depth": self._calculate_nesting_depth(tree.root_node),
            "num_parameters": self._count_parameters(tree.root_node, code),
        }
        
        # Add complexity rating
        cc = metrics["cyclomatic_complexity"]
        if cc <= 5:
            metrics["complexity_rating"] = "simple"
        elif cc <= 10:
            metrics["complexity_rating"] = "moderate"
        elif cc <= 20:
            metrics["complexity_rating"] = "complex"
        else:
            metrics["complexity_rating"] = "very complex"
        
        return metrics
    
    def _calculate_cyclomatic_complexity(self, node: Node, complexity: int = 1) -> int:
        """Calculate cyclomatic complexity."""
        
        decision_nodes = {
            "if_statement",
            "for_statement", 
            "while_statement",
            "except_clause",
            "with_statement",
            "boolean_operator",
            "conditional_expression"
        }
        
        if node.type in decision_nodes:
            complexity += 1
        
        for child in node.children:
            complexity = self._calculate_cyclomatic_complexity(child, complexity)
        
        return complexity
    
    def _calculate_nesting_depth(self, node: Node, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        
        nesting_nodes = {
            "if_statement",
            "for_statement",
            "while_statement",
            "with_statement",
            "try_statement",
            "function_definition",
            "class_definition"
        }
        
        if node.type in nesting_nodes:
            current_depth += 1
        
        max_depth = current_depth
        for child in node.children:
            child_depth = self._calculate_nesting_depth(child, current_depth)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def _count_parameters(self, node: Node, source_code: str) -> int:
        """Count number of function parameters."""
        
        if node.type == "function_definition":
            params_node = node.child_by_field_name("parameters")
            if params_node:
                count = 0
                for child in params_node.children:
                    if child.type == "identifier":
                        text = self._get_node_text(child, source_code)
                        if text != "self":
                            count += 1
                return count
        
        return 0
    
    def extract_docstring(self, code: str) -> Optional[str]:
        """Extract existing docstring from code if present."""
        
        tree = self.parser.parse(bytes(code, "utf8"))
        
        for node in tree.root_node.children:
            if node.type in ["function_definition", "class_definition"]:
                body = node.child_by_field_name("body")
                if body and body.children:
                    first_stmt = body.children[0]
                    if first_stmt.type == "expression_statement":
                        string_node = first_stmt.children[0] if first_stmt.children else None
                        if string_node and string_node.type == "string":
                            docstring = self._get_node_text(string_node, code)
                            # Remove quotes and clean up
                            docstring = docstring.strip('"""').strip("'''").strip()
                            return docstring
        
        return None
    
    def get_function_signature(self, code: str) -> Optional[str]:
        """Extract function signature (name and parameters)."""
        
        tree = self.parser.parse(bytes(code, "utf8"))
        
        for node in tree.root_node.children:
            if node.type == "function_definition":
                name = node.child_by_field_name("name")
                params = node.child_by_field_name("parameters")
                
                if name and params:
                    name_text = self._get_node_text(name, code)
                    params_text = self._get_node_text(params, code)
                    return f"{name_text}{params_text}"
        
        return None