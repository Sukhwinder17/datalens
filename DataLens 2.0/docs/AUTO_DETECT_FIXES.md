# DataLens — Automatic Detection & Robustness Fixes

This build keeps the existing UI and architecture, while hardening the data path.

## What is fixed

- CSV and XLSX use one universal loading/profiling pipeline.
- CSV delimiter detection supports comma, semicolon, tab and pipe files.
- Common CSV encodings are attempted automatically.
- Recoverable malformed CSV rows no longer crash the profiler; the Python parser logs skipped physical rows.
- Duplicate column headers are safely disambiguated without dropping columns.
- XLSX automatically selects the most data-rich readable worksheet.
- Empty Excel/title sheets are preserved in workbook metadata while the best data sheet is selected.
- Pandas/NumPy statistics remain defensive around NaN, infinity, empty and constant columns.
- Matplotlib plot endpoints remain compatible with arbitrary datasets.
- Frontend profiling and visualization errors now surface the backend detail when available.
- Visualization image failures show a useful UI message instead of an unexplained blank panel.
- Regression tests cover deep profiling, XLSX sheet selection, malformed CSV recovery, duplicate headers and Matplotlib output.

## Run from Windows CMD

From the extracted project folder:

```cmd
START_DATALENS.cmd
```

Or manually:

```cmd
cd /d "...\DataLens_PROFESSIONAL_AUTO_DETECT_FIXEDackend"
python -m venv venv
call venv\Scriptsctivate
python -m pip install --timeout 600 --retries 10 -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open a second CMD:

```cmd
cd /d "...\DataLens_PROFESSIONAL_AUTO_DETECT_FIXEDrontend"
npm install
npm run dev
```

The existing frontend routes and API structure are intentionally retained.
