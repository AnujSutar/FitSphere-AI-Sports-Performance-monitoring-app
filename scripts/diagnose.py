"""Local setup diagnostics: python scripts/diagnose.py [--camera]"""
import argparse, importlib, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['app.py','requirements.txt','database/connection.py','auth/authentication.py','modules/personal_fitness.py','modules/athlete_dashboard.py','vision/rep_counter.py','data/sample_players.csv']
PKGS=['streamlit','pandas','numpy','plotly','sklearn','cv2','openpyxl','pytest']
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--camera',action='store_true'); args=parser.parse_args(); failed=False
    print(f'Python: {sys.version.split()[0]} ({sys.executable})')
    if sys.version_info < (3,10) or sys.version_info >= (3,13): print('WARN: use Python 3.10–3.12')
    for name in REQUIRED:
        ok=(ROOT/name).is_file(); print(f'{"OK" if ok else "MISSING"} file {name}'); failed |= not ok
    for mod in PKGS:
        try:
            m=importlib.import_module(mod); print(f'OK dependency {mod}: {getattr(m,"__version__","available")}')
        except Exception as e: print(f'MISSING dependency {mod}: {e}'); failed=True
    try:
        db=ROOT/'data'/'diagnostic.sqlite'; conn=sqlite3.connect(db); conn.execute('CREATE TABLE IF NOT EXISTS healthcheck(value INTEGER)'); conn.execute('INSERT INTO healthcheck VALUES(1)'); conn.commit(); conn.close(); db.unlink(missing_ok=True); print('OK SQLite create/write/delete')
    except Exception as e: print(f'FAIL SQLite: {e}'); failed=True
    try:
        import mediapipe as mp; print('OK MediaPipe:',getattr(mp,'__version__','available'))
    except Exception as e: print(f'OPTIONAL MediaPipe unavailable: {e}')
    try:
        import cv2; cap=cv2.VideoCapture(0)
        if cap.isOpened():
            ok,_=cap.read(); cap.release(); print('OK camera frame captured' if ok else 'WARN camera opened but no frame captured')
        else: cap.release(); print('WARN camera unavailable or permission denied')
    except Exception as e: print(f'WARN camera check failed: {e}')
    print('Camera access can also be reviewed in Windows Settings > Privacy & security > Camera.')
    print('Diagnostics:', 'FAIL' if failed else 'completed (review optional warnings)')
    return int(failed)
if __name__=='__main__': raise SystemExit(main())
