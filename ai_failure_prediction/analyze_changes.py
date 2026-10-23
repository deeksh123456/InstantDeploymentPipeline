
from pathlib import Path
import ast
import json
import sys


def analyze_python_files():
    root = Path.cwd()
    excluded_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
    }

    python_files = []

    for path in root.rglob("*.py"):
        if any(part in excluded_dirs for part in path.parts):
            continue

        # Ignore files inside this helper's generated/cache folders.
        python_files.append(path)

    total_files = len(python_files)
    syntax_errors = []
    total_lines = 0

    for path in python_files:
        try:
            source = path.read_text(encoding="utf-8")
            total_lines += len(source.splitlines())
            ast.parse(source, filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as error:
            syntax_errors.append({
                "file": str(path.relative_to(root)),
                "error": str(error),
            })
        except OSError as error:
            syntax_errors.append({
                "file": str(path.relative_to(root)),
                "error": str(error),
            })

    result = {
        "analysis_type": "source_snapshot",
        "python_files_found": total_files,
        "total_python_lines": total_lines,
        "syntax_errors": syntax_errors,
        "syntax_check": "PASS" if not syntax_errors else "FAIL",
        "exact_changed_files_detected": False,
    }

    print(json.dumps(result, indent=2))

    if total_files == 0 or syntax_errors:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(analyze_python_files())
