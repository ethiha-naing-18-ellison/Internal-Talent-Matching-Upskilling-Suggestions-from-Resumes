python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host "Dev env ready. Run: uvicorn backend.app:app --reload"
