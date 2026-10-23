
import argparse
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "model" / "deployment_risk_model.joblib"


def main():
    parser = argparse.ArgumentParser(
        description="Predict demo deployment failure risk."
    )
    parser.add_argument(
        "--build-status",
        choices=["success", "failed"],
        required=True,
    )
    parser.add_argument(
        "--tests-passed",
        choices=["yes", "no"],
        required=True,
    )
    parser.add_argument("--changed-files", type=int, required=True)
    parser.add_argument("--previous-failures", type=int, required=True)
    parser.add_argument("--duration-minutes", type=float, required=True)

    args = parser.parse_args()

    if (
        args.changed_files < 0
        or args.previous_failures < 0
        or args.duration_minutes < 0
    ):
        parser.error("numeric inputs cannot be negative")

    if not MODEL_PATH.exists():
        raise SystemExit(
            "Model not found. Run `python train_model.py` first."
        )

    model = joblib.load(MODEL_PATH)

    sample = pd.DataFrame(
        [
            {
                "build_status": args.build_status,
                "tests_passed": args.tests_passed,
                "changed_files": args.changed_files,
                "previous_failures": args.previous_failures,
                "duration_minutes": args.duration_minutes,
            }
        ]
    )

    probabilities = model.predict_proba(sample)[0]
    classes = list(model.classes_)

    failure_probability = float(
        probabilities[classes.index("failure")]
    )

    predicted_outcome = (
        "FAILURE RISK"
        if failure_probability >= 0.5
        else "LOWER FAILURE RISK"
    )

    if failure_probability >= 0.70:
        band = "HIGH"
    elif failure_probability >= 0.40:
        band = "MEDIUM"
    else:
        band = "LOW"

    reasons = []

    if args.build_status == "failed":
        reasons.append("the build status is failed")

    if args.tests_passed == "no":
        reasons.append("tests did not pass")

    if args.previous_failures >= 2:
        reasons.append("there are multiple previous failures")

    if args.changed_files >= 15:
        reasons.append("many files changed")

    if args.duration_minutes >= 8:
        reasons.append("deployment/build duration is relatively long")

    print("\n=== AI-Based Deployment Risk (demo) ===")
    print(f"Predicted outcome: {predicted_outcome}")
    print(f"Failure probability: {failure_probability:.1%}")
    print(f"Risk band: {band}")

    print("\nSignals to review:")

    if reasons:
        for reason in reasons:
            print(f"- Review because {reason}.")
    else:
        print("- No configured warning signals were triggered.")

    print(
        "\nRecommendation: Inspect logs and tests before deployment. "
        "Do not rely on this demo model alone to approve production."
    )
    print(
        "NOTE: This model was trained on synthetic example data, "
        "not your real deployment history."
    )

    if band == "HIGH":
        print(
            "\nBLOCKED: High deployment risk. "
            "The validation stage must stop."
        )
        raise SystemExit(1)

    print("\nValidation gate: PASSED risk threshold check.")


if __name__ == "__main__":
    main()
