# FitSphere AI

Local-first Streamlit project for personal fitness management and multi-sport performance exploration.

## Windows environment
Recommended: Windows 10/11, 64-bit CPython 3.12, 16 GB RAM. The current workspace uses Python 3.12.3, Streamlit 1.64.0 and OpenCV contrib 4.10.0.84, all import successfully. MediaPipe and pytest are absent in this environment. OpenCV wheels support Python 3.12; MediaPipe availability varies by release and Python ABI, so install it only in a Python 3.12 venv after confirming a compatible wheel is published. Do not replace OpenCV with multiple `opencv-*` distributions in one environment; this project declares contrib as its sole OpenCV package. Streamlit has no webcam bridge requirement here: OpenCV opens the local camera from the Python process.

## PowerShell setup
Run in the project directory:
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python scripts/diagnose.py
python -m compileall -q app.py auth database fitness modules utils vision
python -m pytest -q
streamlit run app.py
```
If script activation is blocked for the current shell, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again. To enable the camera check explicitly, run `python scripts/diagnose.py --camera`; it attempts camera index 0 and releases it. Camera access requires a connected camera and Windows camera permission.

## Features
- PBKDF2-SHA256 account registration and login, profile settings and user-scoped fitness data.
- Workout/activity logging, weight history, charts, plan CRUD with exercise editing, and goal CRUD with progress/status/target dates.
- Rule-based routine suggestions.
- MediaPipe Pose/OpenCV squat counter implementation with knee-angle transitions and clear dependency/camera errors. Actual operation requires compatible MediaPipe and camera.
- Multi-sport interest selection: football (soccer), cricket, basketball, field hockey, tennis, volleyball, table tennis, baseball, kabaddi and badminton.
- Football dashboard, profiles, comparison, valuation, scouting, and performance charts use the bundled synthetic football records. A separate clearly labelled synthetic demo dataset now includes ten sample athletes per selected sport, with sport-specific sample stat columns, roster tables, comparisons and charts. These records are fictional and must not be presented as real athletes or results.
- CSV/Excel import preview and reporting exports.
- Dark/light appearance setting and adjustable text/control scale in Settings.

## Dependencies
`requirements.txt` includes runtime packages with bounded major versions. `requirements-dev.txt` adds pytest. `opencv-contrib-python` supplies OpenCV APIs and is declared instead of installing duplicate OpenCV distributions. MediaPipe is intentionally optional because availability is Python-version/platform-wheel dependent; install it separately only when a compatible Windows wheel exists.

## Database
SQLite is initialized at `data/fitsphere.db`. Tables include users, profiles, sessions, workout records, activities, weight history, goals, plans and plan exercises. User IDs constrain fitness queries; foreign keys cascade plan/session records. Schema initialization migrates older fitness goals to include target dates.

## Verify/start
`python scripts/diagnose.py` checks project files, runtime dependencies, SQLite write access, optional MediaPipe and camera availability. Then run the compile, pytest and Streamlit commands above. Successful CLI startup is not the same as verified browser/HTTP access; check the URL printed by Streamlit in your local browser.

## Model and data limitations
Valuation compares Linear Regression, Random Forest and Gradient Boosting with MAE, RMSE and R² on a seeded holdout split. The small dataset is synthetic; metrics are not real scouting evidence or market estimates. No third-party player dataset or images are included.

## Screenshots
Add screenshots captured from your own local run.

## Verification notes
Workspace Python compilation and direct CRUD/isolation/migration workflows have passed. Pytest execution, webcam operation and local HTTP access have not been verified in the restricted environment; diagnostics will report local dependency and camera state. Install/test on the target Windows laptop before presenting webcam functionality as working.

## Multi-sport scope
The workspace supports ten selectable sports: football, cricket, basketball, field hockey, tennis, volleyball, table tennis, baseball, kabaddi and badminton. `data/sample_multisport.csv` provides ten synthetic demo entries for each non-football sport with sport-labelled sample measures for roster exploration, comparisons and charts. Football retains its dedicated player dataset and ML valuation workflow. Synthetic values are illustrative, not real athlete records or official performance statistics.

## Sign-in design
The login screen uses ssets/login_gym_wallpaper.png, a generated fitness-themed background with a dark overlay for text contrast. This image is original project artwork; no external image source is required.


## UI references applied
The supplied Stitch variants informed the app styling: Kinetic Obsidian dark navy/green theme, Kinetic Daylight light surfaces/green primary actions, and wide dashboard spacing for desktop. User theme and scale are stored in the local `user_preferences` SQLite table. Mobile styles retain stacked Streamlit columns. Screen images are references; interactive behavior remains implemented in Streamlit widgets.

## Recent fixes
Excel template/report exports use an explicit in-memory `ExcelWriter` for compatibility with current Pandas. Data import preview reports missing values, data types, unique values and duplicates, and exports cleaned CSV/XLSX copies. Seller listings record the owner user ID; sellers can only remove their own listings.

Marketplace demo workflow verification: seller-owned listing creation and local demo order/cart-clear transaction passed a direct SQLite check. No real payment or external order is created.

## Stitch UI rebuild status
The shared UI applies the Stitch color tokens and component treatment across every Streamlit page: sidebar navigation, headings, metrics, cards, forms, controls, tabs, alerts, uploaders, tables, and download buttons. Desktop mode uses a wide dashboard canvas; Mobile mode uses a narrow single-column canvas and alternate navigation. Plotly selects its theme from the saved appearance setting. Existing module workflows remain connected. Visual matching has not been verified through a live browser here, so compare locally against the supplied Stitch screenshots before claiming pixel-level parity.

## Real cricket data workflow
The Cricket workspace can ingest a user-provided Cricsheet JSON match file or JSON ZIP archive, derive match-level player batting/bowling summaries, visualize the results, and export a CSV that includes source and license columns. Cricsheet JSON is made available under the Open Data Commons Attribution License (ODC-BY 1.0); attribution is required. See https://cricsheet.org/licensing/ and https://cricsheet.org/downloads/. Imported files are processed in memory during the Streamlit session; the project does not bundle or redistribute a match archive. The other sports' included roster data remains synthetic demo data.

