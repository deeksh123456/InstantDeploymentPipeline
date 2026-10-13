
import ast
import sys
import tokenize
from pathlib import Path


def analyze_python_file(file_path):
    path = Path(file_path)

    if not path.is_file():
        print(f"ERROR: File not found: {path}")
        return False

    if path.suffix != ".py":
        print("ERROR: Only Python files (.py) are supported.")
        return False

    try:
        with tokenize.open(str(path)) as source_file:
            source_code = source_file.read()

        ast.parse(source_code, filename=str(path))

        print("\n=== AI Code Analysis Report ===")
        print(f"File: {path.name}")
        print("Syntax check: PASSED")
        print("Result: PASS")
        print("No Python syntax errors detected.")
        print(
            "Note: Runtime errors and logical errors "
            "may still exist."
        )
        return True

    except SyntaxError as error:
        print("\n=== AI Code Analysis Report ===")
        print(f"File: {path.name}")
        print("Syntax check: FAILED")
        print("Result: FAIL")
        print(f"Error: {error.msg}")
        print(f"Line: {error.lineno}")
        print(f"Column: {error.offset}")
        print("\nSuggestion:")
        print("Review the indicated line for missing colons,")
        print("unclosed brackets, incorrect indentation, or")
        print("other Python syntax mistakes.")
        return False

    except (OSError, UnicodeError, tokenize.TokenError) as error:
        print(f"ERROR: Could not analyze file: {error}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python code_analyzer.py <python_file>")
        sys.exit(2)

    success = analyze_python_file(sys.argv[1])
    sys.exit(0 if success else 1)
