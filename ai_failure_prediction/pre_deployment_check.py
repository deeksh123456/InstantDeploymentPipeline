
import argparse
import re
import subprocess
import sys
from pathlib import Path


def run_check(command):
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Local pre-deployment checks"
    )
    parser.add_argument("file", help="Python file to check")
    parser.add_argument(
        "--build-status",
        choices=["success", "failed"],
        default="success",
    )
    parser.add_argument(
        "--tests-passed",
        choices=["yes", "no"],
        default="yes",
    )
    parser.add_argument("--changed-files", type=int, default=1)
    parser.add_argument("--previous-failures", type=int, default=0)
    parser.add_argument("--duration-minutes", type=float, default=3)

    args = parser.parse_args()
    target = Path(args.file)

    if not target.is_file() or target.suffix != ".py":
        print("FINAL RESULT: BLOCKED")
        print("Provide an existing Python file.")
        return 1

    print("\n=== 1. Syntax Check ===")
    syntax = run_check(
        [sys.executable, "code_analyzer.py", str(target)]
    )
    print(syntax.stdout, end="")

    if syntax.returncode != 0:
        print("\nFINAL RESULT: BLOCKED")
        print("Reason: Syntax check failed.")
        return 1

    print("\n=== 2. Code Quality Check ===")
    quality = run_check(
        [sys.executable, "quality_check.py", str(target)]
    )
    print(quality.stdout, end="")

    if quality.returncode != 0:
        print("\nFINAL RESULT: BLOCKED")
        print("Reason: Code-quality check failed.")
        return 1

    print("\n=== 3. Build and Test Status ===")

    if args.build_status == "failed":
        print("Build status: FAILED")

    if args.tests_passed == "no":
        print("Tests status: FAILED")

    if args.build_status == "failed" or args.tests_passed == "no":
        print("\nFINAL RESULT: BLOCKED")
        print("Reason: Build or tests failed.")
        return 1

    print("Build status: SUCCESS")
    print("Tests status: PASSED")

    print("\n=== 4. Deployment Risk Prediction ===")
    prediction = run_check(
        [
            sys.executable,
            "predict.py",
            "--build-status", args.build_status,
            "--tests-passed", args.tests_passed,
            "--changed-files", str(args.changed_files),
            "--previous-failures", str(args.previous_failures),
            "--duration-minutes", str(args.duration_minutes),
        ]
    )
    print(prediction.stdout, end="")

    if prediction.returncode != 0:
        print("\nFINAL RESULT: BLOCKED")
        print("Reason: Risk prediction could not be completed.")
        return 1

    match = re.search(
        r"Risk band:\s*(LOW|MEDIUM|HIGH)",
        prediction.stdout,
        re.IGNORECASE,
    )

    if not match:
        print("\nFINAL RESULT: MANUAL REVIEW")
        print("Could not determine the risk band.")
        return 2

    risk = match.group(1).upper()

    if risk == "HIGH":
        print("\nFINAL RESULT: MANUAL REVIEW")
        print("High predicted risk: obtain approval before deployment.")
        return 2

    if risk == "MEDIUM":
        print("\nFINAL RESULT: MANUAL REVIEW")
        print("Medium predicted risk: review before deployment.")
        return 2

    print("\nFINAL RESULT: ELIGIBLE")
    print("Checks passed and the demo model reported LOW risk.")
    print("This does not itself deploy the application.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
