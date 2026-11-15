import sqlite3
from config import DB_PATH

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c

def init_db():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS user_profiles(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,age INTEGER,height_cm REAL,weight_kg REAL,experience TEXT,goal TEXT,equipment TEXT,days_per_week INTEGER,duration_min INTEGER);
        CREATE TABLE IF NOT EXISTS workout_sessions(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,workout_date TEXT NOT NULL,name TEXT NOT NULL,duration_min INTEGER NOT NULL,notes TEXT);
        CREATE TABLE IF NOT EXISTS workout_records(id INTEGER PRIMARY KEY,session_id INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,exercise TEXT NOT NULL,sets INTEGER,reps INTEGER,weight_kg REAL);
        CREATE TABLE IF NOT EXISTS activity_logs(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,activity_date TEXT NOT NULL,activity TEXT NOT NULL,duration_min INTEGER,steps INTEGER,notes TEXT);
        CREATE TABLE IF NOT EXISTS weight_history(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,recorded_on TEXT NOT NULL,weight_kg REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS fitness_goals(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,title TEXT NOT NULL,target REAL,current REAL DEFAULT 0,unit TEXT,status TEXT DEFAULT 'Active');
        CREATE TABLE IF NOT EXISTS workout_plans(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,name TEXT NOT NULL,description TEXT DEFAULT '',days_per_week INTEGER DEFAULT 3,duration_min INTEGER DEFAULT 45,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS plan_exercises(id INTEGER PRIMARY KEY,plan_id INTEGER NOT NULL REFERENCES workout_plans(id) ON DELETE CASCADE,exercise TEXT NOT NULL,instructions TEXT DEFAULT '',sets INTEGER DEFAULT 3,reps INTEGER DEFAULT 10,rest_seconds INTEGER DEFAULT 60);
        CREATE TABLE IF NOT EXISTS shop_products(id INTEGER PRIMARY KEY,name TEXT NOT NULL,category TEXT NOT NULL,description TEXT NOT NULL,price REAL NOT NULL,unit TEXT NOT NULL,tag TEXT DEFAULT 'Demo listing');
        CREATE TABLE IF NOT EXISTS shop_wishlist(user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,product_id INTEGER NOT NULL REFERENCES shop_products(id) ON DELETE CASCADE,PRIMARY KEY(user_id,product_id));
        CREATE TABLE IF NOT EXISTS shop_orders(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,subtotal REAL NOT NULL,status TEXT NOT NULL DEFAULT 'Demo order',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS shop_order_items(order_id INTEGER NOT NULL REFERENCES shop_orders(id) ON DELETE CASCADE,product_name TEXT NOT NULL,quantity INTEGER NOT NULL,unit_price REAL NOT NULL,PRIMARY KEY(order_id,product_name));
        CREATE TABLE IF NOT EXISTS shop_cart(user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,product_id INTEGER NOT NULL REFERENCES shop_products(id) ON DELETE CASCADE,quantity INTEGER NOT NULL DEFAULT 1,PRIMARY KEY(user_id,product_id));
        CREATE TABLE IF NOT EXISTS user_preferences(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,theme TEXT NOT NULL DEFAULT 'Dark',ui_scale INTEGER NOT NULL DEFAULT 110,layout_mode TEXT NOT NULL DEFAULT 'Desktop');
        CREATE INDEX IF NOT EXISTS idx_plans_user ON workout_plans(user_id);
        CREATE INDEX IF NOT EXISTS idx_goals_user_status ON fitness_goals(user_id,status);
        CREATE INDEX IF NOT EXISTS idx_sessions_user_date ON workout_sessions(user_id,workout_date);
        CREATE INDEX IF NOT EXISTS idx_activity_user_date ON activity_logs(user_id,activity_date);
        """)
        cols={r[1] for r in c.execute("PRAGMA table_info(fitness_goals)")}
        if "target_date" not in cols: c.execute("ALTER TABLE fitness_goals ADD COLUMN target_date TEXT")
        pref_cols={r[1] for r in c.execute("PRAGMA table_info(user_preferences)")}
        if "layout_mode" not in pref_cols: c.execute("ALTER TABLE user_preferences ADD COLUMN layout_mode TEXT NOT NULL DEFAULT 'Desktop'")
        product_cols={r[1] for r in c.execute("PRAGMA table_info(shop_products)")}
        if "seller_id" not in product_cols: c.execute("ALTER TABLE shop_products ADD COLUMN seller_id INTEGER REFERENCES users(id) ON DELETE CASCADE")
