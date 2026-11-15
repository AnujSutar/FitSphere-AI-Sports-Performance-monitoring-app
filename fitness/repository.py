from database.connection import connect

def create_plan(uid,name,description='',days=3,duration=45):
    with connect() as c:
        cur=c.execute('INSERT INTO workout_plans(user_id,name,description,days_per_week,duration_min) VALUES(?,?,?,?,?)',(uid,name.strip(),description.strip(),days,duration))
        return cur.lastrowid
def list_plans(uid):
    with connect() as c: return [dict(x) for x in c.execute('SELECT * FROM workout_plans WHERE user_id=? ORDER BY id',(uid,))]
def update_plan(uid,pid,name,description,days,duration):
    with connect() as c: return c.execute('UPDATE workout_plans SET name=?,description=?,days_per_week=?,duration_min=? WHERE id=? AND user_id=?',(name,description,days,duration,pid,uid)).rowcount==1
def delete_plan(uid,pid):
    with connect() as c: return c.execute('DELETE FROM workout_plans WHERE id=? AND user_id=?',(pid,uid)).rowcount==1
def add_plan_exercise(uid,pid,exercise,instructions='',sets=3,reps=10,rest=60):
    with connect() as c:
        if not c.execute('SELECT 1 FROM workout_plans WHERE id=? AND user_id=?',(pid,uid)).fetchone(): return None
        cur=c.execute('INSERT INTO plan_exercises(plan_id,exercise,instructions,sets,reps,rest_seconds) VALUES(?,?,?,?,?,?)',(pid,exercise,instructions,sets,reps,rest)); return cur.lastrowid
def remove_plan_exercise(uid,pid,eid):
    with connect() as c:
        if not c.execute('SELECT 1 FROM workout_plans WHERE id=? AND user_id=?',(pid,uid)).fetchone(): return False
        return c.execute('DELETE FROM plan_exercises WHERE id=? AND plan_id=?',(eid,pid)).rowcount==1
def list_plan_exercises(uid,pid):
    with connect() as c: return [dict(x) for x in c.execute('SELECT e.* FROM plan_exercises e JOIN workout_plans p ON p.id=e.plan_id WHERE p.user_id=? AND p.id=?',(uid,pid))]
def create_goal(uid,title,target,unit,target_date=None):
    with connect() as c:
        cur=c.execute("INSERT INTO fitness_goals(user_id,title,target,current,unit,status,target_date) VALUES(?,?,?,0,?,'Active',?)",(uid,title,target,unit,target_date)); return cur.lastrowid
def list_goals(uid):
    with connect() as c: return [dict(x) for x in c.execute('SELECT * FROM fitness_goals WHERE user_id=? ORDER BY id',(uid,))]
def update_goal(uid,gid,title,target,current,unit,status,target_date):
    with connect() as c: return c.execute('UPDATE fitness_goals SET title=?,target=?,current=?,unit=?,status=?,target_date=? WHERE id=? AND user_id=?',(title,target,current,unit,status,target_date,gid,uid)).rowcount==1
def delete_goal(uid,gid):
    with connect() as c: return c.execute('DELETE FROM fitness_goals WHERE id=? AND user_id=?',(gid,uid)).rowcount==1
