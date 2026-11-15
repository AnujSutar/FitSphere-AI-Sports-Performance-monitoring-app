import pandas as pd
import streamlit as st
from database.connection import connect
from modules.personal_fitness import query

def reports_page(uid):
    st.markdown("<div class='eyebrow'>REPORTING</div><h1>Your data, ready to take with you</h1>",unsafe_allow_html=True)
    workouts=query("SELECT workout_date,name,duration_min,notes FROM workout_sessions WHERE user_id=? ORDER BY workout_date DESC",(uid,))
    activities=query("SELECT activity_date,activity,duration_min,steps,notes FROM activity_logs WHERE user_id=? ORDER BY activity_date DESC",(uid,))
    for label,df in [('Workout history',workouts),('Activity history',activities)]:
        st.subheader(label)
        if df.empty: st.caption('No entries to export yet.')
        else: st.download_button(f'Download {label.lower()} CSV',df.to_csv(index=False).encode('utf-8'),file_name=label.lower().replace(' ','_')+'.csv',mime='text/csv')
    if not workouts.empty or not activities.empty:
        import io
        output=io.BytesIO()
        with pd.ExcelWriter(output,engine='openpyxl') as writer:
            workouts.to_excel(writer,index=False,sheet_name='Workouts'); activities.to_excel(writer,index=False,sheet_name='Activities')
        st.download_button('Download personal report Excel',output.getvalue(),file_name='fitsphere_personal_report.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.subheader('Football demo report'); players=pd.read_csv('data/sample_players.csv'); st.download_button('Download synthetic player dataset CSV',players.to_csv(index=False).encode(),file_name='synthetic_players.csv',mime='text/csv')
