from auth.authentication import register_user, authenticate
from database.connection import init_db

def test_password_hash_login(tmp_path, monkeypatch):
    import database.connection as db
    monkeypatch.setattr(db, 'DB_PATH', tmp_path / 'auth.db')
    init_db()
    assert register_user('Test User','test@example.test','safe-password')[0]
    assert authenticate('test@example.test','safe-password')
    assert authenticate('test@example.test','wrong-password') is None
