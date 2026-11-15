from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA = Path(__file__).resolve().parents[1] / 'data' / 'sample_players.csv'
MULTISPORT_DATA = Path(__file__).resolve().parents[1] / 'data' / 'sample_multisport.csv'
SPORTS = ['Football (Soccer)', 'Cricket', 'Basketball', 'Field Hockey', 'Tennis', 'Volleyball', 'Table Tennis', 'Baseball', 'Kabaddi', 'Badminton']
@st.cache_data
def load():
    return pd.read_csv(DATA)

@st.cache_data
def load_multisport():
    return pd.read_csv(MULTISPORT_DATA)

def show_sport_demo(sport):
    if sport=='Cricket':
        show_cricsheet_workspace()
        return
    data=load_multisport(); df=data[data.sport==sport].copy()
    if df.empty:
        st.warning('No sample records exist for this sport yet.'); return
    metric_cols=[c for c in df.columns if c not in ('sport','name','discipline','team','age','events','rating')]
    a,b,c,d=st.columns(4); a.metric('Demo athletes',len(df)); b.metric('Average age',f'{df.age.mean():.1f}'); c.metric('Events recorded',int(df.events.sum())); d.metric('Average rating',f'{df.rating.mean():.1f}/10')
    st.caption('Synthetic demonstration records, not real athlete statistics. Metrics are illustrative and vary by sport.')
    st.subheader(f'{sport} sample roster')
    st.dataframe(df,hide_index=True,use_container_width=True)
    x,y=st.columns(2)
    if metric_cols:
        x.plotly_chart(px.bar(df,x='name',y=metric_cols[0],color='team',template=st.session_state.get('plotly_template','plotly_dark'),title=metric_cols[0]+' by athlete'),use_container_width=True)
        y.plotly_chart(px.scatter(df,x=metric_cols[0],y=metric_cols[-1],color='team',hover_name='name',template=st.session_state.get('plotly_template','plotly_dark'),title=metric_cols[0]+' vs '+metric_cols[-1]),use_container_width=True)
    athletes=st.multiselect('Compare demo athletes',df.name,default=df.name.iloc[:2].tolist(),key=f'compare_{sport}')
    if athletes:
        st.dataframe(df[df.name.isin(athletes)],hide_index=True,use_container_width=True)

def show_cricsheet_workspace():
    from sports.cricsheet import parse_upload
    st.subheader('Cricket performance · Cricsheet match data')
    st.caption('Upload a Cricsheet JSON match file or JSON ZIP archive. The app calculates player batting and bowling summaries locally; the archive is not sent to a service.')
    st.markdown('**Source:** [Cricsheet downloads](https://cricsheet.org/downloads/) · **License:** JSON data is released under Open Data Commons Attribution (ODC-BY 1.0). Please keep attribution when sharing derived outputs.')
    uploaded=st.file_uploader('Upload Cricsheet JSON or ZIP',type=['json','zip'],key='cricsheet_upload')
    if not uploaded:
        st.info('Upload Cricsheet data to view real match summaries. Other sports continue to show clearly labelled fictional demo entries.')
        return
    try:
        rows=parse_upload(uploaded.name,uploaded.getvalue())
        events=pd.DataFrame(rows)
        grouped=events.groupby('player',as_index=False).agg(matches=('match_id','nunique'),runs=('runs','sum'),balls_faced=('balls_faced','sum'),fours=('fours','sum'),sixes=('sixes','sum'),wickets=('wickets','sum'),runs_conceded=('runs_conceded','sum'),balls_bowled=('balls_bowled','sum'))
        grouped['strike_rate']=(grouped.runs*100/grouped.balls_faced.replace(0,float('nan'))).round(2)
        grouped['economy']=(grouped.runs_conceded*6/grouped.balls_bowled.replace(0,float('nan'))).round(2)
        grouped['data_source']='Cricsheet (uploaded by user)'
        grouped['data_license']='Open Data Commons Attribution License 1.0 (ODC-BY 1.0)'
        grouped['source_url']='https://cricsheet.org/downloads/'
        st.success(f'Loaded {events.match_id.nunique()} match(es), {len(grouped)} players. Aggregates are derived from uploaded ball-by-ball records.')
        a,b,c,d=st.columns(4); a.metric('Players',len(grouped)); b.metric('Runs',int(grouped.runs.sum())); c.metric('Wickets',int(grouped.wickets.sum())); d.metric('Matches',events.match_id.nunique())
        st.dataframe(grouped.sort_values(['runs','wickets'],ascending=False),hide_index=True,use_container_width=True)
        x,y=st.columns(2)
        x.plotly_chart(px.bar(grouped.nlargest(10,'runs'),x='player',y='runs',template=st.session_state.get('plotly_template','plotly_dark'),title='Top run scorers'),use_container_width=True)
        y.plotly_chart(px.scatter(grouped,x='runs',y='wickets',size='balls_faced',hover_name='player',template=st.session_state.get('plotly_template','plotly_dark'),title='Batting and wickets'),use_container_width=True)
        st.download_button('Export player summary CSV',grouped.to_csv(index=False).encode('utf-8'),file_name='cricsheet_player_summary.csv',mime='text/csv')
    except Exception as exc: st.error(f'Could not process this Cricsheet file: {exc}')

def athlete_page():
    df = load()
    st.markdown("<div class='eyebrow'>ATHLETE INTELLIGENCE · MULTI-SPORT</div><h1>Sports performance workspace</h1>", unsafe_allow_html=True)
    selected = st.multiselect('Choose sports you follow', SPORTS, default=st.session_state.get('favorite_sports', ['Football (Soccer)']), key='favorite_sports')
    active = st.selectbox('Sport workspace', selected or SPORTS, key='active_sport')
    if active != 'Football (Soccer)':
        show_sport_demo(active)
        return
    tabs = st.tabs(['Dashboard', 'Player profiles', 'Compare', 'Valuation', 'Scouting', 'Performance'])
    with tabs[0]:
        pos = st.multiselect('Positions', sorted(df.position.unique()), default=sorted(df.position.unique()))
        f = df[df.position.isin(pos)]
        a,b,c,d = st.columns(4)
        a.metric('Players', len(f)); b.metric('Average age', f'{f.age.mean():.1f}' if len(f) else '—'); c.metric('Average value', f'€{f.market_value_m.mean():.1f}m' if len(f) else '—'); d.metric('Top scorer', f.loc[f.goals.idxmax(),'name'] if len(f) else '—')
        x,y = st.columns(2)
        x.plotly_chart(px.pie(f, names='position', hole=.58, template=st.session_state.get('plotly_template','plotly_dark'), title='Position mix'), use_container_width=True)
        y.plotly_chart(px.scatter(f, x='goals', y='market_value_m', color='position', hover_name='name', size='appearances', template=st.session_state.get('plotly_template','plotly_dark'), title='Goals and market value'), use_container_width=True)
        st.caption('All player data in this starter dataset is synthetic and exists for demonstration only.')
    with tabs[1]:
        name = st.selectbox('Choose a player', df.name); row = df[df.name == name].iloc[0]
        st.subheader(name); st.caption(f'{row.club} · {row.position} · {row.nationality} · Age {row.age}')
        a,b,c,d = st.columns(4); a.metric('Appearances',int(row.appearances)); b.metric('Goals',int(row.goals)); c.metric('Assists',int(row.assists)); d.metric('Market value',f'€{row.market_value_m:.1f}m')
        q = pd.DataFrame({'Metric':['Goals / 90','Assists / 90'],'Rate':[row.goals*90/row.minutes if row.minutes else 0,row.assists*90/row.minutes if row.minutes else 0]})
        st.plotly_chart(px.bar(q,x='Metric',y='Rate',template=st.session_state.get('plotly_template','plotly_dark'),title='Output per 90 minutes'),use_container_width=True)
    with tabs[2]:
        picks=st.multiselect('Select two or more players',df.name,default=df.name.iloc[:2].tolist(),max_selections=5)
        if len(picks)>=2:
            comp=df[df.name.isin(picks)].copy(); comp['goals_per90']=comp.goals*90/comp.minutes; comp['assists_per90']=comp.assists*90/comp.minutes
            st.dataframe(comp[['name','position','age','appearances','goals','assists','goals_per90','assists_per90','market_value_m']].round(2),hide_index=True,use_container_width=True)
            st.plotly_chart(px.bar(comp,x='name',y=['goals','assists'],barmode='group',template=st.session_state.get('plotly_template','plotly_dark'),title='Goals and assists'),use_container_width=True)
            if comp.position.nunique()>1: st.info('Players have different listed positions; role and playing time affect direct comparisons.')
    with tabs[3]:
        st.subheader('Market value estimate'); st.caption('Synthetic demo data only, not official market prices. Small training data makes estimates highly uncertain.')
        features=['age','position','appearances','goals','assists','minutes']; num=[x for x in features if x!='position']
        pre=ColumnTransformer([('num',Pipeline([('imp',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),('cat',OneHotEncoder(handle_unknown='ignore'),['position'])])
        models={'Linear regression':LinearRegression(),'Random forest':RandomForestRegressor(n_estimators=150,max_depth=5,random_state=42),'Gradient boosting':GradientBoostingRegressor(random_state=42)}
        if len(df)>8:
            Xtr,Xte,ytr,yte=train_test_split(df[features],df.market_value_m,test_size=.25,random_state=42); results=[]
            for n,m in models.items():
                pipe=Pipeline([('pre',pre),('model',m)]); pipe.fit(Xtr,ytr); pred=pipe.predict(Xte); results.append({'Model':n,'MAE (€m)':mean_absolute_error(yte,pred),'RMSE (€m)':mean_squared_error(yte,pred)**.5,'R²':r2_score(yte,pred)})
            st.dataframe(pd.DataFrame(results).round(3),hide_index=True,use_container_width=True)
            chosen=st.selectbox('Model used for estimate',list(models)); model=Pipeline([('pre',pre),('model',models[chosen])]); model.fit(df[features],df.market_value_m)
            with st.form('valuation'):
                c1,c2,c3=st.columns(3); age=c1.number_input('Age',16,45,23); position=c2.selectbox('Position',sorted(df.position.unique())); apps=c3.number_input('Appearances',0,60,20); goals=c1.number_input('Goals',0,80,8); assists=c2.number_input('Assists',0,50,5); minutes=c3.number_input('Minutes',0,6000,1500)
                if st.form_submit_button('Estimate value'):
                    value=float(model.predict(pd.DataFrame([[age,position,apps,goals,assists,minutes]],columns=features))[0]); st.success(f'Estimated value: €{max(0,value):.2f} million')
        else: st.warning('More sample rows are required to train this demo model.')
    with tabs[4]:
        st.subheader('Scouting filters'); c1,c2,c3=st.columns(3); maxage=c1.slider('Maximum age',16,40,25); positions=c2.multiselect('Positions',sorted(df.position.unique()),default=sorted(df.position.unique()),key='scout_pos'); maxval=c3.slider('Maximum listed value (€m)',0.0,float(df.market_value_m.max()),float(df.market_value_m.max()))
        f=df[(df.age<=maxage)&df.position.isin(positions)&(df.market_value_m<=maxval)].copy()
        if len(f):
            features=['age','position','appearances','goals','assists','minutes']; pre2=ColumnTransformer([('num',SimpleImputer(strategy='median'),['age','appearances','goals','assists','minutes']),('cat',OneHotEncoder(handle_unknown='ignore'),['position'])]); pipe=Pipeline([('pre',pre2),('model',RandomForestRegressor(n_estimators=100,max_depth=4,random_state=7))]).fit(df[features],df.market_value_m); f['model_estimate_m']=pipe.predict(f[features]); f['estimate_gap_m']=f.model_estimate_m-f.market_value_m
            st.dataframe(f.sort_values('estimate_gap_m',ascending=False)[['name','club','position','age','goals','assists','market_value_m','model_estimate_m','estimate_gap_m']].round(2),hide_index=True,use_container_width=True)
            st.caption('Estimate gap = model estimate minus synthetic listed value. This is exploratory, not evidence a player is truly undervalued.')
        else: st.info('No players match these filters.')
    with tabs[5]:
        x,y=st.columns(2); x.plotly_chart(px.box(df,x='position',y='goals',color='position',template=st.session_state.get('plotly_template','plotly_dark'),title='Goals by position'),use_container_width=True); y.plotly_chart(px.scatter(df,x='age',y='market_value_m',color='position',hover_name='name',template=st.session_state.get('plotly_template','plotly_dark'),title='Age and market value'),use_container_width=True)
