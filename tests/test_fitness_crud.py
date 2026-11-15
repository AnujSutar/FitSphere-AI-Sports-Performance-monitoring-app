import pytest
import database.connection as db
from fitness import repository as repo

@pytest.fixture
def users(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DB_PATH',tmp_path/'crud.db'); db.init_db()
    with db.connect() as c:
        c.execute("INSERT INTO users(name,email,password_hash) VALUES('A','a@test','x')")
        c.execute("INSERT INTO users(name,email,password_hash) VALUES('B','b@test','x')")
    return 1,2

def test_plan_full_crud_exercises_and_isolation(users):
    a,b=users; pid=repo.create_plan(a,'Base','desc',3,40)
    assert repo.list_plans(a)[0]['name']=='Base' and repo.list_plans(b)==[]
    eid=repo.add_plan_exercise(a,pid,'Squat','brace',4,8,90)
    assert repo.list_plan_exercises(a,pid)[0]['exercise']=='Squat'
    assert repo.list_plan_exercises(b,pid)==[]
    assert repo.update_plan(a,pid,'Strength','new',4,50)
    assert not repo.update_plan(b,pid,'Hacked','',1,1)
    assert repo.remove_plan_exercise(a,pid,eid)
    assert not repo.remove_plan_exercise(b,pid,eid)
    assert repo.delete_plan(a,pid) and repo.list_plans(a)==[]
    assert not repo.delete_plan(b,pid)

def test_goal_crud_dates_progress_completion_isolation(users):
    a,b=users; gid=repo.create_goal(a,'Walk',20,'km','2027-01-01')
    goal=repo.list_goals(a)[0]; assert goal['status']=='Active' and goal['target_date']=='2027-01-01'; assert repo.list_goals(b)==[]
    assert repo.update_goal(a,gid,'Walk more',30,12,'km','Completed','2027-02-01')
    assert not repo.update_goal(b,gid,'hack',0,0,'','Active',None)
    goal=repo.list_goals(a)[0]; assert (goal['title'],goal['current'],goal['target_date'],goal['status'])==('Walk more',12,'2027-02-01','Completed')
    assert repo.delete_goal(a,gid) and repo.list_goals(a)==[]
    assert not repo.delete_goal(b,gid)

def test_old_database_migration(tmp_path,monkeypatch):
    monkeypatch.setattr(db,'DB_PATH',tmp_path/'old.db')
    with db.connect() as c:
        c.execute('CREATE TABLE users(id INTEGER PRIMARY KEY,name TEXT,email TEXT,password_hash TEXT)')
        c.execute('CREATE TABLE fitness_goals(id INTEGER PRIMARY KEY,user_id INTEGER,title TEXT,target REAL,current REAL,unit TEXT,status TEXT)')
        c.execute("INSERT INTO users VALUES(1,'Old','old@test','x')")
        c.execute("INSERT INTO fitness_goals VALUES(1,1,'Legacy',10,2,'km','Active')")
    db.init_db()
    with db.connect() as c:
        assert 'target_date' in {r[1] for r in c.execute('PRAGMA table_info(fitness_goals)')}
        assert c.execute('SELECT title FROM fitness_goals').fetchone()[0]=='Legacy'
