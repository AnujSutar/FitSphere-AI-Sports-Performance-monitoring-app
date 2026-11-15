from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st
from database.connection import connect
from auth.authentication import profile

def query(sql, args):
    with connect() as c: return pd.read_sql_query(sql, c, params=args)

def fitness_page(uid):
    st.markdown("<div class='eyebrow'>PERSONAL FITNESS</div><h1>Your training, made visible</h1>", unsafe_allow_html=True)
    t1,t2,t3,t4,t5,t6=st.tabs(["Dashboard","Log workout","Activity","Progress","Workout plans","Goals & insights"])
    sessions=query("SELECT * FROM workout_sessions WHERE user_id=? ORDER BY workout_date DESC",(uid,))
    with t1:
        recent=sessions[sessions.workout_date>=str(date.today()-timedelta(days=6))] if not sessions.empty else sessions
        p=profile(uid); w=float(p.get("weight_kg") or 0); h=float(p.get("height_cm") or 0); bmi=w/(h/100)**2 if w and h else None
        a,b,c,d=st.columns(4); a.metric("Current weight",f"{w:g} kg" if w else "—"); b.metric("BMI",f"{bmi:.1f}" if bmi else "—"); c.metric("Workouts · 7 days",len(recent)); d.metric("Training time · 7 days",f"{int(recent.duration_min.sum()) if not recent.empty else 0} min")
        if bmi: st.caption("BMI is a rough screening measure based on height and weight; it does not account for body composition or individual health context.")
        st.subheader("Recent training")
        if sessions.empty: st.info("Log your first workout to see your training history here.")
        else:
            daily=sessions.groupby("workout_date",as_index=False).agg(minutes=("duration_min","sum"),sessions=("id","count")); fig=px.bar(daily,x="workout_date",y="minutes",labels={"workout_date":"Date","minutes":"Minutes"},template=st.session_state.get('plotly_template','plotly_dark'),color_discrete_sequence=["#58a6ff"]); fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=5,r=5,t=10,b=5)); st.plotly_chart(fig,use_container_width=True); st.dataframe(sessions.head(8),hide_index=True,use_container_width=True)
    with t2:
        st.subheader("Record a workout")
        with st.form("workout_log"):
            name=st.text_input("Workout name",placeholder="Strength session"); dt=st.date_input("Date",date.today()); mins=st.number_input("Duration (minutes)",1,600,45); exercise=st.text_input("Exercise",placeholder="Goblet squat"); sets=st.number_input("Sets",0,30,3); reps=st.number_input("Repetitions",0,200,10); load=st.number_input("Weight used (kg)",0.0,500.0,0.0); notes=st.text_area("Notes",height=70)
            if st.form_submit_button("Save workout",use_container_width=True):
                if not name.strip(): st.error("Add a workout name.")
                else:
                    with connect() as c:
                        cur=c.execute("INSERT INTO workout_sessions(user_id,workout_date,name,duration_min,notes) VALUES(?,?,?,?,?)",(uid,str(dt),name.strip(),int(mins),notes.strip()))
                        if exercise.strip(): c.execute("INSERT INTO workout_records(session_id,exercise,sets,reps,weight_kg) VALUES(?,?,?,?,?)",(cur.lastrowid,exercise.strip(),int(sets),int(reps),float(load)))
                    st.success("Workout saved"); st.rerun()
        if not sessions.empty:
            with st.expander("Workout history"):
                st.dataframe(sessions,hide_index=True,use_container_width=True)
                choice=st.selectbox("Select workout to remove",sessions.apply(lambda r:f"{r['workout_date']} · {r['name']} (#{r['id']})",axis=1))
                if st.button("Delete selected workout"):
                    sid=int(choice.rsplit("#",1)[1].rstrip(")"))
                    with connect() as c: c.execute("DELETE FROM workout_sessions WHERE id=? AND user_id=?",(sid,uid))
                    st.rerun()
    with t3:
        st.subheader("Daily activity")
        with st.form("activity_log"):
            dt=st.date_input("Activity date",date.today(),key="actdate"); activity=st.selectbox("Activity",["Walking","Running","Cycling","Other"]); duration=st.number_input("Duration (minutes)",0,1440,30); steps=st.number_input("Steps (optional)",0,100000,0); notes=st.text_input("Notes",key="actnotes")
            if st.form_submit_button("Save activity"):
                with connect() as c: c.execute("INSERT INTO activity_logs(user_id,activity_date,activity,duration_min,steps,notes) VALUES(?,?,?,?,?,?)",(uid,str(dt),activity,int(duration),int(steps) or None,notes.strip()))
                st.success("Activity saved"); st.rerun()
        acts=query("SELECT activity_date,activity,duration_min,steps,notes FROM activity_logs WHERE user_id=? ORDER BY activity_date DESC",(uid,))
        if acts.empty: st.info("Activity is entered manually; this app does not connect to a device or measure steps automatically.")
        else:
            st.dataframe(acts,hide_index=True,use_container_width=True); byday=acts.groupby("activity_date",as_index=False).duration_min.sum(); st.plotly_chart(px.line(byday,x="activity_date",y="duration_min",markers=True,template=st.session_state.get('plotly_template','plotly_dark'),labels={"activity_date":"Date","duration_min":"Activity minutes"}),use_container_width=True)
    with t4:
        st.subheader("Weight history"); weights=query("SELECT recorded_on,weight_kg FROM weight_history WHERE user_id=? ORDER BY recorded_on",(uid,))
        if weights.empty: st.info("Add your height and weight in Settings to begin a weight history.")
        else: st.plotly_chart(px.line(weights,x="recorded_on",y="weight_kg",markers=True,template=st.session_state.get('plotly_template','plotly_dark'),labels={"recorded_on":"Date","weight_kg":"Weight (kg)"}),use_container_width=True); st.dataframe(weights,hide_index=True,use_container_width=True)
        st.caption("Progress views are based only on records you have entered.")
    with t5:
        st.subheader("Workout plans")
        plans=query("SELECT * FROM workout_plans WHERE user_id=? ORDER BY id DESC",(uid,))
        with st.form("create_plan"):
            pname=st.text_input("Plan name"); desc=st.text_area("Description"); pdays=st.number_input("Days per week",1,7,3); pdur=st.number_input("Session length (minutes)",10,180,45)
            if st.form_submit_button("Create plan"):
                if pname.strip():
                    with connect() as c: c.execute("INSERT INTO workout_plans(user_id,name,description,days_per_week,duration_min) VALUES(?,?,?,?,?)",(uid,pname.strip(),desc.strip(),pdays,pdur))
                    st.rerun()
        if not plans.empty:
            selected=st.selectbox("Saved plan",plans.id,format_func=lambda x:plans.loc[plans.id==x,"name"].iloc[0],key="plan_id")
            plan=plans[plans.id==selected].iloc[0]
            with st.form("edit_plan"):
                ename=st.text_input("Edit name",plan["name"]); edesc=st.text_area("Edit description",plan["description"]); edays=st.number_input("Edit days/week",1,7,int(plan.days_per_week)); edur=st.number_input("Edit duration",10,180,int(plan.duration_min))
                if st.form_submit_button("Save plan changes"):
                    with connect() as c: c.execute("UPDATE workout_plans SET name=?,description=?,days_per_week=?,duration_min=? WHERE id=? AND user_id=?",(ename.strip(),edesc.strip(),edays,edur,selected,uid))
                    st.rerun()
            exercises=query("SELECT * FROM plan_exercises WHERE plan_id=?",(selected,)); st.dataframe(exercises,hide_index=True,use_container_width=True)
            with st.form("add_exercise"):
                ex=st.text_input("Exercise name"); inst=st.text_input("Instructions"); sets=st.number_input("Sets",1,20,3); reps=st.number_input("Reps",1,100,10); rest=st.number_input("Rest (seconds)",0,600,60)
                if st.form_submit_button("Add exercise") and ex.strip():
                    with connect() as c: c.execute("INSERT INTO plan_exercises(plan_id,exercise,instructions,sets,reps,rest_seconds) VALUES(?,?,?,?,?,?)",(selected,ex.strip(),inst.strip(),sets,reps,rest))
                    st.rerun()
            if not exercises.empty:
                remove=st.selectbox("Exercise to remove",exercises.id,format_func=lambda x:exercises.loc[exercises.id==x,"exercise"].iloc[0])
                if st.button("Remove exercise"):
                    with connect() as c: c.execute("DELETE FROM plan_exercises WHERE id=? AND plan_id=?",(remove,selected))
                    st.rerun()
            if st.checkbox("Confirm plan deletion",key="confirm_plan_delete") and st.button("Delete plan",type="primary"):
                with connect() as c: c.execute("DELETE FROM workout_plans WHERE id=? AND user_id=?",(selected,uid))
                st.rerun()
    with t6:
        st.subheader("Fitness goals")
        goals=query("SELECT * FROM fitness_goals WHERE user_id=? ORDER BY id DESC",(uid,))
        with st.form("create_goal"):
            title=st.text_input("Goal title"); target=st.number_input("Target",min_value=0.1,value=10.0); unit=st.text_input("Unit",value="sessions"); due=st.date_input("Target date",key="goal_due")
            if st.form_submit_button("Create goal") and title.strip():
                with connect() as c: c.execute("INSERT INTO fitness_goals(user_id,title,target,current,unit,status,target_date) VALUES(?,?,?,?,?,'Active',?)",(uid,title.strip(),target,0,unit,str(due)))
                st.rerun()
        if not goals.empty:
            st.dataframe(goals,hide_index=True,use_container_width=True)
            gid=st.selectbox("Goal to manage",goals.id,format_func=lambda x:goals.loc[goals.id==x,"title"].iloc[0])
            g=goals[goals.id==gid].iloc[0]
            with st.form("update_goal"):
                nt=st.text_input("Title",g.title); targ=st.number_input("Target",min_value=.1,value=float(g.target)); curr=st.number_input("Progress",min_value=0.,value=float(g.current)); unit2=st.text_input("Unit",g.unit); due2=st.date_input("Target date",value=pd.to_datetime(g.target_date).date() if g.target_date else date.today()); status=st.selectbox("Status",["Active","Completed"],index=1 if g.status=="Completed" else 0)
                if st.form_submit_button("Save goal"):
                    with connect() as c: c.execute("UPDATE fitness_goals SET title=?,target=?,current=?,unit=?,status=?,target_date=? WHERE id=? AND user_id=?",(nt.strip(),targ,curr,unit2.strip(),status,str(due2),gid,uid))
                    st.rerun()
            if st.button("Delete goal"):
                with connect() as c: c.execute("DELETE FROM fitness_goals WHERE id=? AND user_id=?",(gid,uid))
                st.rerun()
        st.subheader("Workout recommendation")
        p=profile(uid); goal=p.get("goal") or "General fitness"; exp=p.get("experience") or "Beginner"; equip=(p.get("equipment") or "Bodyweight").lower(); days=int(p.get("days_per_week") or 3); mins=int(p.get("duration_min") or 45)
        st.subheader("Starting point from your profile"); st.write(f"Goal: **{goal}** · Experience: **{exp}** · Equipment: **{p.get('equipment') or 'Bodyweight'}**")
        if "strength" in goal.lower() or "muscle" in goal.lower(): recs=["Squat variation · 3 × 8–12","Push-up or press variation · 3 × 8–12","Hip hinge variation · 3 × 8–12","Rest 60–120 seconds; choose a manageable load"]
        elif "endurance" in goal.lower(): recs=["Brisk walk, jog or cycle · 20–30 minutes","Use a pace that lets you speak in short sentences","Add time gradually as it feels comfortable"]
        else: recs=["Full-body movement session · 20–30 minutes","Bodyweight squat · 3 × 8–12","Incline push-up · 3 × 6–10","Brisk walk · 15–25 minutes"]
        if "bodyweight" in equip: recs=[x.replace("press variation","incline push-up") for x in recs]
        st.markdown("**Example routine**"); st.caption(f"A general starting suggestion for {days} days per week and about {mins} minutes per session."); st.markdown("\n".join(f"- {r}" for r in recs)); st.info("General fitness information only; adjust to your comfort and seek qualified advice for medical or rehabilitation needs.")
        st.markdown("**Exercise counter**")
        try:
            import mediapipe
            if st.button("Start squat counter",key="start_squat_camera"):
                from vision.rep_counter import run_camera
                error=run_camera()
                if error: st.error(error)
        except ImportError:
            st.warning("MediaPipe is not installed, so webcam counting cannot run in this environment. Install a Python 3.12-compatible MediaPipe wheel, then restart the app. The counter uses knee-angle transitions and does not claim posture or injury assessment.")
