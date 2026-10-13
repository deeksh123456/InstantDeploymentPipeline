# AI-Based Failure Prediction and Analysis (Objective 5)

This is a local starter MVP for the Instant Deployment Pipeline project. It trains a small ML classifier on example CI/CD history and predicts a deployment risk from build/test status, number of changed files, previous failures, and deployment duration.

## Important
- `data/deployment_history.csv` contains **synthetic demo data**, not real records from your AWS account.
- The model is for a project prototype, not a production-grade reliability decision. Replace the demo data with real pipeline/deployment records before claiming real predictive accuracy.
- This first step runs locally and does not require starting either EC2 instance or changing AWS resources.

## 1. Requirements
- Python 3.10 or newer recommended
- Internet access only to install the Python package the first time

## 2. Open a terminal in this folder
Windows: open the folder in File Explorer, click the address bar, type `cmd`, and press Enter.

## 3. Create a virtual environment (recommended)
```bat
python -m venv .venv
.venv\Scripts\activate
```

If `python` is not recognized, try `py` instead.

## 4. Install dependencies
```bat
python -m pip install -r requirements.txt
```

## 5. Train and evaluate the demo model
```bat
python train_model.py
```

## 6. Make a sample prediction
```bat
python predict.py --build-status success --tests-passed yes --changed-files 3 --previous-failures 0 --duration-minutes 2.5
```

Try a riskier example:
```bat
python predict.py --build-status failed --tests-passed no --changed-files 18 --previous-failures 3 --duration-minutes 12
```

## What happens
1. `train_model.py` loads the CSV and trains a Logistic Regression classifier.
2. It reports a simple holdout accuracy and saves the model to `model/deployment_risk_model.joblib`.
3. `predict.py` loads the saved model and prints predicted outcome, risk band, probability, and a basic rule-based explanation.

## Next implementation steps
1. Replace synthetic history with actual deployment records.
2. Add code/test scanning results as features if needed.
3. Add a CodeBuild stage to run analysis and fail the stage when policy says deployment must be blocked.
4. Keep manual approval after the analysis stage.
