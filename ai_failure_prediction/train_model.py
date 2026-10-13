from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "deployment_history.csv"
MODEL_PATH = ROOT / "model" / "deployment_risk_model.joblib"

FEATURES = [
    "build_status", "tests_passed", "changed_files",
    "previous_failures", "duration_minutes"
]
CATEGORICAL = ["build_status", "tests_passed"]
NUMERIC = ["changed_files", "previous_failures", "duration_minutes"]

def main():
    df = pd.read_csv(DATA)
    X = df[FEATURES]
    y = df["outcome"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore"))
            ]), CATEGORICAL),
            ("numeric", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scale", StandardScaler())
            ]), NUMERIC)
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    print(f"Demo holdout accuracy: {accuracy_score(y_test, predictions):.2%}")
    print("\nDemo classification report:")
    print(classification_report(y_test, predictions, zero_division=0))

    # Refit on all available data for the saved demo model.
    model.fit(X, y)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nSaved model to: {MODEL_PATH}")
    print("NOTE: scores reflect synthetic demo data only; they do not establish real AWS deployment accuracy.")

if __name__ == "__main__":
    main()
