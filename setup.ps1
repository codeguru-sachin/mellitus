# One-time setup for Windows PowerShell:   .\setup.ps1
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
Write-Host "Setup finished. Next: python run_pipeline.py"
