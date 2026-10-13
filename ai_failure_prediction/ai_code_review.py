
import argparse
import re
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


def run(command):
    """Run a command from the project directory."""
    try:
        return subprocess.run(
            command,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            check=False,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        print(f"ERROR: Command timed out: {command[0]}")
        return None
    except OSError as error:
        print(f"ERROR: Could not run command: {error}")
        return None


def show_result(result):
    if result is None:
        return False

    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(result.stderr, end="")

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="AI-assisted pre-deployment code review"
    )
    parser.add_argument("file")
    parser.add_argument("--changed-files", type=int, default=1)
    parser.add_argument("--previous-failures", type=int, default=0)
    parser.add_argument("--duration-minutes", type=float, default=3)
    args = parser.parse_args()

    target = Path(args.file).expanduser().resolve()

    if not target.is_file() or target.suffix.lower() != ".py":
        print("FINAL RESULT: BLOCKED")
        print("Provide an existing Python file.")
        return 1

    # 1. Syntax validation
    print("\n=== 1. Syntax Validation ===")
    syntax = run([
        sys.executable,
        str(PROJECT_DIR / "code_analyzer.py"),
        str(target),
    ])

    if not show_result(syntax):
        print("\nFINAL RESULT: BLOCKED")
        print("Reason: Syntax validation failed.")
        print("Fix the error before requesting AI suggestions.")
        return 1

    # 2. Code quality
    print("\n=== 2. Code Quality ===")
    quality = run([
        sys.executable,
        str(PROJECT_DIR / "quality_check.py"),
        str(target),
    ])

    if not show_result(quality):
        print("\nFINAL RESULT: BLOCKED")
        print("Reason: Code-quality check failed.")
        return 1

    # 3. Actual Python compilation check
    print("\n=== 3. Python Compilation Check ===")
    compilation = run([
        sys.executable,
        "-m",
        "py_compile",
        str(target),
    ])

    if not show_result(compilation):
        print("\nFINAL RESULT: BLOCKED")
        print("Reason: Python compilation failed.")
        return 1

    print("Compilation status: PASSED")

    # 4. Run real automated tests
    print("\n=== 4. Automated Tests (pytest) ===")
    tests = run([
        sys.executable,
        "-m",
        "pytest",
        "-q",
    ])

    if not show_result(tests):
        print("\nFINAL RESULT: BLOCKED")
        print("Reason: Automated tests failed or pytest could not run.")
        return 1

    print("Tests status: PASSED")
    print("Note: The pytest suite ran successfully.")

    # 5. AI suggestions are advisory, not proof of correctness
    print("\n=== 5. AI Code Suggestions ===")
    review = run([
        sys.executable,
        str(PROJECT_DIR / "code_suggester.py"),
        str(target),
    ])

    if not show_result(review):
        print("\nFINAL RESULT: MANUAL REVIEW")
        print("Reason: AI review could not be completed.")
        return 2

    # 6. Predict deployment risk using verified check outcomes
    print("\n=== 6. Deployment Risk Prediction ===")
    prediction = run([
        sys.executable,
        str(PROJECT_DIR / "predict.py"),
        "--build-status", "success",
        "--tests-passed", "yes",
        "--changed-files", str(args.changed_files),
        "--previous-failures", str(args.previous_failures),
        "--duration-minutes", str(args.duration_minutes),
    ])

    if not show_result(prediction):
        print("\nFINAL RESULT: MANUAL REVIEW")
        print("Reason: Risk prediction could not be completed.")
        return 2

    match = re.search(
        r"Risk band:\s*(LOW|MEDIUM|HIGH)",
        prediction.stdout,
        re.IGNORECASE,
    )

    if not match or match.group(1).upper() != "LOW":
        print("\nFINAL RESULT: MANUAL REVIEW")
        print("Review the risk result before considering deployment.")
        return 2

    print("\nFINAL RESULT: ELIGIBLE")
    print("Compilation and automated tests passed.")
    print("Static checks passed and the demo model reported LOW risk.")
    print("AI suggestions still require developer review.")
    print("No deployment has been performed.")
    print(
        "IMPORTANT: The risk model uses synthetic demo data; "
        "this result does not guarantee safe deployment."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
