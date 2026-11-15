import hashlib, hmac, os, re
from database.connection import connect

def _hash(password,salt=None):
    salt=salt or os.urandom(16); digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,310000); return salt.hex()+":"+digest.hex()
def _verify(password,stored):
    try: salt,digest=stored.split(":"); return hmac.compare_digest(_hash(password,bytes.fromhex(salt)).split(":")[1],digest)
    except Exception: return False
def register_user(name,email,password):
    name=name.strip(); email=email.strip().lower()
    if len(name)<2 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",email): return False,"Enter a name and valid email."
    if len(password)<8: return False,"Use a password with at least 8 characters."
    try:
        with connect() as c: c.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",(name,email,_hash(password)))
        return True,"Created"
    except Exception: return False,"An account with that email may already exist."
def authenticate(email,password):
    with connect() as c: row=c.execute("SELECT id,name,password_hash FROM users WHERE email=?",(email.strip().lower(),)).fetchone()
    return (row["id"],row["name"]) if row and _verify(password,row["password_hash"]) else None
def profile(uid):
    with connect() as c: row=c.execute("SELECT * FROM user_profiles WHERE user_id=?",(uid,)).fetchone()
    return dict(row) if row else {}
def save_profile(uid,age,height,weight,experience,goal,equipment,days,duration):
    with connect() as c:
        c.execute("INSERT INTO user_profiles VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET age=excluded.age,height_cm=excluded.height_cm,weight_kg=excluded.weight_kg,experience=excluded.experience,goal=excluded.goal,equipment=excluded.equipment,days_per_week=excluded.days_per_week,duration_min=excluded.duration_min",(uid,age,height,weight,experience,goal,equipment,days,duration))
        if weight>0: c.execute("INSERT INTO weight_history(user_id,recorded_on,weight_kg) VALUES(?,date('now'),?)",(uid,weight))
