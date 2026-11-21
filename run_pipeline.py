"""One command for the whole data-science part:   python run_pipeline.py

 1. download + validate the dataset      4. SHAP / permutation importance
 2. exploratory data analysis (EDA)      5. (then start the API and the dashboard)
 3. train + compare + save the models
"""
import sys

from src import download_data, eda, explain, train


def step(n: int, title: str) -> None:
    print(f"\n{'=' * 70}\nSTEP {n}: {title}\n{'=' * 70}")


if __name__ == "__main__":
    step(1, "Dataset")
    download_data.main()
    step(2, "Exploratory data analysis")
    eda.run_eda()
    step(3, "Training and model comparison")
    train.run_training()
    step(4, "Explainability")
    explain.main()
    print("\nAll done. Next:\n  Terminal 1: uvicorn backend.main:app --reload\n"
          "  Terminal 2: streamlit run frontend/app.py")
    sys.exit(0)
