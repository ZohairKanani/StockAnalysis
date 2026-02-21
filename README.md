StockAnalysis
=============

Quick project overview
- Small project to fetch S&P 500 historical data from Yahoo Finance and run simple trading strategies (momentum implemented).

Project layout
- data/                     -> CSVs (tickers, historical data)
- notebook/                 -> your working notebook (left unchanged)
- src/data_fetch.py         -> function `fetch_sp500_data()` to download and save data
- src/trading_strategies.py -> interactive runner with `momentum_strategy()`
- src/fama_french.py      -> compute UMD factor and run Fama-French 4-factor analysis

Prerequisites
- Python 3.8+ (recommended)
- virtual environment (optional but recommended)

Quick start
1. Create and activate a venv (Windows PowerShell):
```powershell
python -m venv .env
.\.env\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
python -m pip install -r requirements.txt
```
If the `pip` launcher is broken (e.g., points to an old path), use `python -m pip` as above.

3. Fetch data (will save a dated CSV into `data/`):
```powershell
python src\data_fetch.py
```

4. Run trading strategies (interactive):
```powershell
python src\trading_strategies.py
```

5. Run Fama-French / UMD analysis (monthly data):
```powershell
setx START_DATE 2018-01-01
setx END_DATE 2025-12-31
python src\fama_french.py
```

Notes
- The code expects `data/sp500_symbols.csv` to exist (list of symbols under a `Symbol` column). Place the file in `data/`.
- The code expects `data/ff_monthly.csv` to exist (Fama-French 3 factors in monthly format). Place the file in `data/`.
- `src/data_fetch.py` resolves paths relative to the project root so you can run scripts from any CWD.
- Use the environment variables `START_DATE` and `END_DATE` (YYYY-MM-DD) to control date range for downloads. If not set, defaults are used.
