# DiaPredict AI - Diabetes Prediction and Risk Assessment System

BCA 5th semester AI & Data Science project. Predicts the likelihood of diabetes from 8 health measurements
using machine learning, explains the prediction (SHAP), stores history in SQLite, and offers a REST API
(FastAPI), a dashboard (Streamlit) and PDF reports.

> **Medical disclaimer:** educational risk-assessment tool, **not** a medical device or diagnosis.
> The score comes from a small research dataset and is not a clinically calibrated personal risk.

## What is inside

| Part | Technology | Location |
|---|---|---|
| Data cleaning, EDA | pandas, seaborn, matplotlib | `src/preprocessing.py`, `src/eda.py` |
| 7 ML models + comparison | scikit-learn, XGBoost | `src/train.py`, `src/evaluate.py` |
| Explainability | SHAP (+ permutation importance) | `src/explain.py` |
| Prediction service | joblib pipeline | `src/predict.py` |
| REST API + Swagger | FastAPI, Pydantic | `backend/` |
| Database | SQLite + SQLAlchemy | `backend/database/` |
| Dashboard | Streamlit, Plotly | `frontend/` |
| PDF report | ReportLab | `backend/services/report_service.py` |
| Tests | pytest | `tests/` |

## 1. Install (Windows 11, VS Code, Python 3.11)

Open the project folder in VS Code, then **Terminal -> New Terminal** (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1          # you should now see (venv) in the prompt
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

(`setup.ps1` does the same steps.) If PowerShell blocks activation:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## 2. Get the data, run EDA, train the models

```powershell
python run_pipeline.py
```

This runs, in order: dataset download + validation -> EDA -> training/comparison of all models -> SHAP/importance.
Or run the steps one by one:

```powershell
python -m src.download_data
python -m src.eda
python -m src.train
python -m src.explain
```

If the automatic download fails, download `diabetes.csv` from Kaggle ("Pima Indians Diabetes Database"),
save it as `data/raw/pima_diabetes.csv` and run `python -m src.download_data` to validate it.
Fill in the licence details in `docs/DATASET_SOURCE.md`.

Results you will find afterwards (all generated from your data):

- `reports/model_comparison.md` / `.csv` - the model comparison report
- `reports/figures/` - EDA charts, ROC, PR, confusion matrices, calibration, SHAP summary
- `models/best_model.joblib` + `models/metadata.json` - selected pipeline and its description
- `notebooks/eda.ipynb`, `notebooks/model_training.ipynb` - the same analysis as notebooks (select the `venv` kernel)

## 3. Run the application (two terminals, both with `(venv)` active)

```powershell
# Terminal 1 - backend API
uvicorn backend.main:app --reload

# Terminal 2 - dashboard
streamlit run frontend/app.py
```

- Dashboard: http://localhost:8501
- API docs (Swagger): http://127.0.0.1:8000/docs

## 4. Run the tests

```powershell
pytest
```

API tests need the trained model (step 2); they are skipped otherwise.

## How the main requirements are met

- **No data leakage:** the median imputer and scaler live inside the sklearn `Pipeline`, so cross-validation refits
  them on each training fold only. The test set is touched once, at the end.
- **Impossible zeros:** zeros in Glucose, BloodPressure, SkinThickness, Insulin and BMI become missing values.
- **Model choice is not by accuracy:** among models with CV ROC-AUC within 0.02 of the best and specificity >= 0.55,
  the highest CV recall wins (`select_best` in `src/train.py`; the reasoning is written into the report).
- **Risk categories:** model score < 0.35 Low, 0.35-0.65 Moderate, >= 0.65 High; class 1 when score >= 0.50.
  Documented in `src/config.py`; these are descriptive bands of the model score, not clinical categories.
- **Calibration:** a calibration plot and Brier score are reported, but probabilities are not recalibrated or
  clinically validated, so the UI calls them "model score / estimated probability".
- **Privacy:** only the 8 clinical inputs and an optional anonymous label are stored (no names or contact details).
- **Input validation:** Pydantic rejects impossible values (e.g. glucose 0, age 5, NaN) with HTTP 422.

## API overview (`/api/v1`)

| Method | Path | Purpose |
|---|---|---|
| POST | `/predictions` | Predict, explain and store |
| GET | `/predictions` | Search / filter history (`q`, `risk_category`, `predicted_class`, dates, age range) |
| GET | `/predictions/export/csv` | CSV export (same filters) |
| GET | `/predictions/{id}` | One prediction |
| GET | `/predictions/{id}/report` | PDF report |
| GET | `/dashboard/stats`, `/dashboard/dataset` | Dashboard data |
| GET | `/models/info`, `/comparison`, `/curves`, `/importance`, `/shap-summary` | Model information |
| GET | `/samples`, `/health` | Sample inputs, health check |

## Known limitations (state these in your viva / report)

- 768 rows, one population (Pima women aged 21+); no external validation.
- Insulin (~49 %) and SkinThickness (~30 %) have many missing values; median imputation is simple.
- Hyper-parameters are sensible defaults, not exhaustively tuned (a natural extension: `GridSearchCV`).
- SHAP values are model explanations, not medical causation.
- SQLite is fine for a single-user demo; use PostgreSQL for multi-user deployment.

## Troubleshooting

| Problem | Fix |
|---|---|
| Dashboard says "API offline" | Start Terminal 1 (`uvicorn ...`) from the project root folder |
| `No trained model found` (HTTP 503) | `python -m src.train` |
| `ModuleNotFoundError: src` / `backend` | Run commands from the project root (the folder containing `backend/`) |
| `shap` fails to install | The app still works: it falls back to permutation importance / occlusion explanations |
| Port 8000 busy | `uvicorn backend.main:app --reload --port 8001` and set `API_URL=http://127.0.0.1:8001` in `.env` |
