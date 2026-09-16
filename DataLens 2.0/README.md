# DataLens 2.0 — Universal Data Profiling & Visualization

DataLens is a local-first data analysis workspace for **CSV and XLSX** files.
It is designed to inspect the actual uploaded data rather than relying on a fixed schema.

## What is included

### Deep profiling
- Row / column / total-cell counts
- Memory usage and data density
- Actual missing cells, missing rows and completely empty rows
- Duplicate rows and duplicate groups
- Column-by-column semantic type detection
- Numeric-like text detection
- Placeholder / blank / whitespace detection
- Constant and near-constant columns
- Possible IDs and imported index columns
- High-cardinality columns
- Mixed-type detection
- Invalid / partially parseable dates
- Numeric statistics: mean, median, mode, variance, standard deviation, percentiles, IQR, fences, skewness, kurtosis, CV, zero/positive/negative counts, infinities and IQR outliers
- Categorical statistics: unique values, top 20, rare values, frequency %, text lengths, blank/whitespace counts
- Correlation matrix and strongest relationships
- Row-level problem investigation

### XLSX support
Excel workbooks are inspected sheet-by-sheet.

DataLens **does not blindly read the first Excel worksheet**. If the first sheet is empty or contains instructions/questions, the loader automatically selects the most data-rich readable worksheet.

For example, a workbook with:
- `Questions` → empty
- `Rajveer Singh` → 300 × 20 data
- pivot/analysis sheets

will automatically use `Rajveer Singh`.

The selected worksheet and detected worksheet count are shown in the UI.

### Visualization Studio
Charts are rendered by **Matplotlib** on the backend:
- Bar
- Line
- Area
- Pie
- Donut
- Scatter
- Histogram
- Box plot

Chart data is prepared with pandas / NumPy and the UI also exposes the generated chart data table.

### Session-scoped uploads
Uploaded files are used for the current DataLens run. The startup launcher clears old raw/cleaned session data before starting the backend, so restarting DataLens gives a clean dataset list and only newly uploaded files appear.

## Project structure

```text
DataLens_updated_functional/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── data_loader.py
│   │   │   ├── data_profiler.py
│   │   │   ├── profile_visuals.py
│   │   │   └── visualization_engine.py
│   │   └── utils/
│   ├── tests/
│   └── requirements.txt
├── datasets/
│   ├── raw/
│   ├── cleaned/
│   └── samples/
├── frontend/
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── pages/
│       ├── services/
│       └── layouts/
├── outputs/
│   ├── charts/
│   ├── exports/
│   └── reports/
├── docs/
├── tests/
├── START_DATALENS.cmd
├── docker-compose.yml
└── README.md
```

## Windows CMD — recommended startup

### Option A: one-click CMD launcher

Double-click:

```text
START_DATALENS.cmd
```

It creates/uses the backend virtual environment, installs Python requirements, starts FastAPI, installs frontend packages if needed, starts Vite, and opens the local application.

### Option B: manual CMD

Open **CMD**, not PowerShell.

#### Terminal 1 — backend

```cmd
cd /d "C:\path\to\DataLens_updated_functional"
if not exist venv\Scripts\python.exe python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
cd /d "C:\path\to\DataLens_updated_functional\backend"
python -m pip install --timeout 600 --retries 10 -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

#### Terminal 2 — frontend

```cmd
cd /d "C:\path\to\DataLens_updated_functional\frontend"
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Important

Do **not** run:

```cmd
cd backend
npm run ml:dev
```

The backend is Python/FastAPI. `npm` belongs to the frontend.

Do **not** create the virtual environment in the wrong nested folder. The intended layout is:

```text
DataLens_updated_functional\
    backend\
    frontend\
    datasets\
    outputs\
    venv\
```

## Verification

Backend tests:

```cmd
cd /d "C:\path\to\DataLens_updated_functional\backend"
call ..\venv\Scripts\activate
python -m pytest -q
```

The current project passes its backend test suite.

## API highlights

```text
GET  /health
GET  /api/datasets
GET  /api/datasets/{id}/profile
GET  /api/datasets/{id}/preview
GET  /api/datasets/{id}/sheets
GET  /api/datasets/{id}/plot
GET  /api/datasets/{id}/problem-rows

POST /api/upload
POST /api/visualization
GET  /api/visualization/plot
```

## Design principles

1. No hard-coded dataset columns.
2. Profile the actual uploaded file.
3. Keep raw uploads unchanged.
4. Treat XLSX worksheets as first-class data sources.
5. Separate API routes, services, schemas, models and utilities.
6. Fail gracefully when a dataset has no compatible values.
7. Render heavy analytical visuals server-side with Matplotlib.
8. Keep the frontend focused on exploration and presentation.


## Professional UI
The existing application structure and data workflow are preserved. The frontend now has a premium DataLens visual layer: glass surfaces, gradient accents, responsive navigation icons, ambient background motion, hover/focus micro-interactions, status animation, and reduced-motion support. No route or backend data structure was intentionally changed.

Run the project by double-clicking `START_DATALENS.cmd` in this root folder.


## Added analysis and dataset-session controls

- **Univariate Analysis**: variable selector, histogram/box plot/category-frequency view, and descriptive statistics.
- **Bivariate Analysis**: two-variable selector, scatter plot, and Pearson correlation.
- **Multivariate Analysis**: three-variable selector, backend-rendered 3D scatter plot, and correlation matrix.
- **Individual dataset delete**: delete one uploaded dataset from the current session and its stored raw upload.
- **Refresh (Clear All)** on the Datasets page: after confirmation, clears every uploaded dataset from the current session.
- **Reload** remains available for a normal non-destructive dataset list refresh.
- The existing one-click `START_DATALENS.cmd` continues to start a clean dataset session and installs frontend packages automatically on first run.
