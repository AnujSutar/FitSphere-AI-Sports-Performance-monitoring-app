import streamlit as st
import pandas as pd
from database.connection import init_db
from auth.authentication import register_user, authenticate, profile, save_profile
from modules.personal_fitness import fitness_page
from modules.athlete_dashboard import athlete_page
from modules.reports import reports_page
from modules.data_management import data_page
from modules.marketplace import marketplace_page
from utils.helpers import inject_styles
from database.connection import connect

st.set_page_config(page_title="FitSphere AI", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
init_db()

if "user_id" not in st.session_state: st.session_state.user_id = None
if "section" not in st.session_state: st.session_state.section = "Overview"
if "layout_mode" not in st.session_state: st.session_state.layout_mode="Desktop"
if st.session_state.user_id is not None:
    with connect() as c:
        pref=c.execute("SELECT theme,ui_scale,layout_mode FROM user_preferences WHERE user_id=?",(st.session_state.user_id,)).fetchone()
        if pref:
            st.session_state.theme=pref["theme"]; st.session_state.ui_scale=pref["ui_scale"]; st.session_state.layout_mode=pref["layout_mode"]
inject_styles()

def auth_screen():
    left, right = st.columns([1.05, .95], gap="large")
    with left:
        st.markdown("<div class='hero'><div class='eyebrow'>PERFORMANCE, IN FOCUS</div><h1>Train with intent.<br><span>Understand your edge.</span></h1><p>One workspace for personal fitness progress and football performance intelligence.</p><div class='hero-chips'><span>FITNESS</span><span>SPORTS ANALYTICS</span><span>PRIVATE BY DESIGN</span></div></div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='panel'>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Sign in", "Create account"])
        with tab1:
            with st.form("login"):
                email=st.text_input("Email"); password=st.text_input("Password",type="password")
                if st.form_submit_button("Continue", use_container_width=True):
                    user=authenticate(email,password)
                    if user: st.session_state.user_id=user[0]; st.session_state.user_name=user[1]; st.rerun()
                    else: st.error("Email or password is incorrect.")
        with tab2:
            with st.form("register"):
                name=st.text_input("Your name"); email=st.text_input("Email address",key="reg_email"); password=st.text_input("Password (8+ characters)",type="password",key="reg_pass")
                if st.form_submit_button("Create account",use_container_width=True):
                    ok,msg=register_user(name,email,password)
                    if ok: st.success("Account created. Sign in to continue.")
                    else: st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.user_id is None:
    auth_screen(); st.stop()

with st.sidebar:
    st.markdown("<div class='brand'>◈ <b>FitSphere</b><small>AI PERFORMANCE PLATFORM</small></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='welcome'>Welcome back<br><b>{st.session_state.user_name}</b></div>",unsafe_allow_html=True)
    pages={"Overview":"◈","Personal Fitness":"⌁","Athlete Intelligence":"◉","Marketplace":"🛍","Reports":"▤","Data Management":"⇧","Settings":"⚙"}
    for label,icon in pages.items():
        if st.button(f"{icon}  {label}",key=f"nav_{label}",use_container_width=True): st.session_state.section=label
    st.markdown("<div class='sidebar-foot'>LOCAL SQLITE · PRIVATE PROFILE</div>",unsafe_allow_html=True)
    if st.button("Log out",use_container_width=True): st.session_state.clear(); st.rerun()

if st.session_state.layout_mode=="Mobile":
    navcols=st.columns(3)
    for i,label in enumerate(["Overview","Personal Fitness","Athlete Intelligence","Marketplace","Reports","Data Management","Settings"]):
        if navcols[i%3].button(label,key=f"mobile_nav_{label}",use_container_width=True): st.session_state.section=label; st.rerun()

section=st.session_state.section
if section=="Overview":
    st.markdown(f"<div class='eyebrow'>YOUR PERFORMANCE WORKSPACE · {st.session_state.user_name.upper()}</div><h1>Train with intent.<br>See your progress.</h1>",unsafe_allow_html=True)
    st.markdown("Your fitness, sports, and gear workspace—built around the activity you care about.")
    with connect() as c:
        wk=c.execute("SELECT COUNT(*),COALESCE(SUM(duration_min),0) FROM workout_sessions WHERE user_id=? AND workout_date>=date('now','-6 days')",(st.session_state.user_id,)).fetchone()
        goal_count=c.execute("SELECT COUNT(*) FROM fitness_goals WHERE user_id=? AND status='Active'",(st.session_state.user_id,)).fetchone()[0]
        cart_count=c.execute("SELECT COALESCE(SUM(quantity),0) FROM shop_cart WHERE user_id=?",(st.session_state.user_id,)).fetchone()[0]
    m1,m2,m3,m4=st.columns(4)
    m1.metric('Workouts · 7 days',wk[0]); m2.metric('Training time',f'{wk[1]} min'); m3.metric('Active goals',goal_count); m4.metric('Cart items',cart_count)
    st.markdown('### Your spaces')
    a,b,c=st.columns(3)
    with a:
        st.markdown("<div class='feature-card'><div class='eyebrow'>01 · PERSONAL FITNESS</div><h2>Build your routine.</h2><p>Plan sessions, track goals and review progress from your own workout records.</p></div>",unsafe_allow_html=True)
        if st.button("Open fitness workspace →",key="go_fitness"): st.session_state.section="Personal Fitness"; st.rerun()
    with b:
        st.markdown("<div class='feature-card violet'><div class='eyebrow'>02 · SPORTS INTELLIGENCE</div><h2>Explore your sport.</h2><p>Choose from ten sports and explore their demo performance workspace.</p></div>",unsafe_allow_html=True)
        if st.button("Explore athlete data →",key="go_athlete"): st.session_state.section="Athlete Intelligence"; st.rerun()
    with c:
        st.markdown("<div class='feature-card'><div class='eyebrow'>03 · MARKETPLACE</div><h2>Find your gear.</h2><p>Browse training equipment, nutrition and snack listings or publish a seller product.</p></div>",unsafe_allow_html=True)
        if st.button("Visit marketplace →",key="go_market"): st.session_state.section="Marketplace"; st.rerun()
elif section=="Personal Fitness": fitness_page(st.session_state.user_id)
elif section=="Athlete Intelligence": athlete_page()
elif section=="Marketplace": marketplace_page()
elif section=="Reports": reports_page(st.session_state.user_id)
elif section=="Data Management": data_page()
elif section=="Settings":
    st.markdown("<div class='eyebrow'>YOUR ACCOUNT</div><h1>Settings</h1>",unsafe_allow_html=True)
    p=profile(st.session_state.user_id)
    st.subheader("Display preferences")
    theme=st.radio("Color theme",["Dark","Light"],horizontal=True,index=0 if st.session_state.get("theme","Dark")=="Dark" else 1,key="settings_theme")
    mode=st.radio("App layout",["Desktop","Mobile"],horizontal=True,index=0 if st.session_state.get("layout_mode","Desktop")=="Desktop" else 1,key="settings_layout")
    st.session_state.ui_scale=st.slider("Text and button size",90,140,int(st.session_state.get("ui_scale",110)),5,format="%d%%")
    st.session_state.theme=theme; st.session_state.layout_mode=mode
    with connect() as c: c.execute("INSERT INTO user_preferences(user_id,theme,ui_scale,layout_mode) VALUES(?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET theme=excluded.theme,ui_scale=excluded.ui_scale,layout_mode=excluded.layout_mode",(st.session_state.user_id,theme,st.session_state.ui_scale,mode))
    st.caption("Theme, app layout and text/control size are saved to your local profile.")
    inject_styles()
    with st.form("profile"):
        age=st.number_input("Age",0,100,int(p.get("age") or 0)); height=st.number_input("Height (cm)",0.0,250.0,float(p.get("height_cm") or 0)); weight=st.number_input("Weight (kg)",0.0,350.0,float(p.get("weight_kg") or 0)); experience=st.selectbox("Experience",["Beginner","Intermediate","Advanced"],index=["Beginner","Intermediate","Advanced"].index(p.get("experience") or "Beginner")); goal=st.selectbox("Fitness goal",["General fitness","Build strength","Improve endurance","Build muscle","Increase activity"]); equipment=st.text_input("Available equipment",p.get("equipment") or "Bodyweight"); days=st.slider("Workout days per week",1,7,int(p.get("days_per_week") or 3)); duration=st.slider("Preferred duration (minutes)",15,120,int(p.get("duration_min") or 45))
        if st.form_submit_button("Save profile"): save_profile(st.session_state.user_id,age,height,weight,experience,goal,equipment,days,duration); st.success("Profile saved")
