
import json
import subprocess
import sys
from pathlib import Path


def check_code(file_name):
    path = Path(file_name)

    if not path.is_file():
        print(f"ERROR: File not found: {path}")
        return False

    if path.suffix != ".py":
        print("ERROR: Please provide a Python (.py) file.")
        return False

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--output-format",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    try:
        issues = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        print("ERROR: Could not read Ruff's analysis result.")
        print(result.stderr)
        return False

    print("\n=== Code Quality Report ===")
    print(f"File: {path.name}")

    if not issues:
        print("Result: PASS")
        print("No Ruff-detectable issues found.")
        print("Note: This does not prove the code is bug-free.")
        return True

    print(f"Result: FAIL ({len(issues)} issue(s) found)")

    for number, issue in enumerate(issues, start=1):
        location = issue.get("location", {})
        line = location.get("row", "?")
        column = location.get("column", "?")
        code = issue.get("code", "UNKNOWN")
        message = issue.get("message", "No description available")
        fix = issue.get("fix")

        print(f"\n{number}. {code}: {message}")
        print(f"   Location: line {line}, column {column}")

        if fix:
            print("   Ruff reports that an automatic fix may be available.")
        else:
            print("   Suggestion: Review this issue and correct it manually.")

    print("\nReview the reported issues before deployment.")
    return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quality_check.py <python_file>")
        sys.exit(2)

    passed = check_code(sys.argv[1])
    sys.exit(0 if passed else 1)
