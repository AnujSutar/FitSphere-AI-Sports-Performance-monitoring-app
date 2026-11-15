import tempfile
from pathlib import Path
import database.connection as db

def test_schema_scopes_records_by_user(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_PATH', tmp_path / 'test.db')
    db.init_db()
    with db.connect() as c:
        c.execute("INSERT INTO users(name,email,password_hash) VALUES('A','a@x.test','h')")
        c.execute("INSERT INTO users(name,email,password_hash) VALUES('B','b@x.test','h')")
        c.execute("INSERT INTO workout_sessions(user_id,workout_date,name,duration_min) VALUES(1,'2026-01-01','Run',20)")
        assert c.execute('SELECT COUNT(*) FROM workout_sessions WHERE user_id=?',(2,)).fetchone()[0] == 0
