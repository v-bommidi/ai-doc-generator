"""Test file processor on our own codebase."""

from src.utils.file_processor import FileProcessor


def test_process_current_project():
    """Test processing our own src/ directory."""
    
    print("\n" + "="*70)
    print("FILE PROCESSOR TEST - Processing src/ directory")
    print("="*70 + "\n")
    
    processor = FileProcessor()
    
    # Process our src directory
    print("Processing src/ directory...\n")
    results = processor.process_directory(
        "src",
        recursive=True,
        exclude_patterns=['__pycache__', 'test_']
    )
    
    # Show results
    print(f"✓ Processed {len(results)} files:\n")
    for file_path, snippets in sorted(results.items()):
        print(f"  {file_path}: {len(snippets)} elements")
    
    # Show statistics
    print("\n" + "="*70)
    stats = processor.get_statistics(results)
    print("Statistics:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total code elements: {stats['total_snippets']}")
    print(f"  Functions: {stats['functions']}")
    print(f"  Classes: {stats['classes']}")
    print(f"  Methods: {stats['methods']}")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_process_current_project()