
import ast
import sys
from pathlib import Path


def validate_python_file(file_name):
    path = Path(file_name)

    if not path.is_file():
        print(f"ERROR: File not found: {path}")
        return False

    if path.suffix.lower() != ".py":
        print("ERROR: Only Python files are supported.")
        return False

    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except SyntaxError as error:
        print("VALIDATION: FAIL")
        print(f"Syntax error: {error.msg}")
        print(f"Line: {error.lineno}, column: {error.offset}")
        return False
    except (OSError, UnicodeError) as error:
        print(f"ERROR: Could not read file: {error}")
        return False

    print("VALIDATION: PASS")
    print("The file has valid Python syntax.")
    print("Note: Syntax validation does not prove correctness.")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_suggestion.py <python_file>")
        sys.exit(2)

    sys.exit(0 if validate_python_file(sys.argv[1]) else 1)
