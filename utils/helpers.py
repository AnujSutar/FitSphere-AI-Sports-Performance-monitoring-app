import streamlit as st
from pathlib import Path
import base64

DARK={"bg":"#0b1326","surface":"#111827","card":"#1e293b","raised":"#222a3d","ink":"#f8fafc","muted":"#bccbb9","edge":"rgba(148,163,184,.16)","primary":"#22c55e","secondary":"#06b6d4","tertiary":"#f59e0b"}
LIGHT={"bg":"#faf8ff","surface":"#ffffff","card":"#f2f3ff","raised":"#e2e7ff","ink":"#131b2e","muted":"#3e4a3d","edge":"#bdcaba","primary":"#00873a","secondary":"#006a61","tertiary":"#00628d"}

def inject_styles():
    dark=st.session_state.get('theme','Dark')=='Dark'; t=DARK if dark else LIGHT
    scale=int(st.session_state.get('ui_scale',110))
    mobile=st.session_state.get('layout_mode','Desktop')=='Mobile'
    st.session_state.plotly_template='plotly_dark' if dark else 'plotly_white'
    wallpaper=''
    if st.session_state.get('user_id') is None:
        image=Path(__file__).resolve().parents[1]/'assets'/'login_gym_wallpaper.png'
        if image.exists():
            b64=base64.b64encode(image.read_bytes()).decode('ascii')
            wallpaper=f"background-image:linear-gradient(90deg,rgba(6,14,32,.94),rgba(6,14,32,.70) 52%,rgba(6,14,32,.28)),url('data:image/png;base64,{b64}');background-size:cover;background-position:center;background-attachment:fixed;"
    mode_css=(f"""section[data-testid=stSidebar]{{display:none}}.block-container{{max-width:540px!important;padding:1rem .85rem 5rem!important;margin:0 auto}}[data-testid=stHorizontalBlock]{{flex-direction:column!important;gap:.65rem!important}}[data-testid=column]{{width:100%!important;min-width:100%!important;flex:1 1 100%!important}}.stTabs [data-baseweb=tab-list]{{overflow-x:auto;flex-wrap:nowrap!important}}.stTabs [data-baseweb=tab]{{white-space:nowrap;min-width:max-content}}[data-testid=stPlotlyChart]{{max-height:340px;overflow:hidden}}h1{{font-size:1.8rem!important}}[data-testid=stMetricValue]{{font-size:1.45rem!important}}""" if mobile else "")
    st.markdown(f'''<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root{{--fs-bg:{t['bg']};--fs-surface:{t['surface']};--fs-card:{t['card']};--fs-raised:{t['raised']};--fs-ink:{t['ink']};--fs-muted:{t['muted']};--fs-edge:{t['edge']};--fs-primary:{t['primary']};--fs-secondary:{t['secondary']};--fs-tertiary:{t['tertiary']};}}
    html,body{{font-family:'DM Sans',sans-serif}}
    .stApp{{background:{t['bg']};{wallpaper}color:{t['ink']};font-size:calc(1rem * {scale/100:.2f})}}
    .block-container{{max-width:1740px;padding:1.8rem clamp(1.3rem,3vw,3.25rem) 4rem}}
    h1,h2,h3,h4{{font-family:Manrope,sans-serif!important;letter-spacing:-.035em;color:{t['ink']}!important}}
    h1{{font-size:clamp(2rem,3vw,2.8rem)!important;font-weight:800!important}} h2{{font-size:1.55rem!important;font-weight:750!important}}
    p,li,label,[data-testid=stMarkdownContainer]{{color:{t['ink']}}}
    section[data-testid=stSidebar]{{background:{t['bg']};border-right:1px solid {t['edge']}}}
    section[data-testid=stSidebar] [data-testid=stButton] button{{width:100%;justify-content:flex-start;min-height:2.75rem;margin:.18rem 0;padding:.65rem .85rem;border:1px solid transparent;border-radius:12px;background:transparent;color:{t['muted']};font-size:1rem;font-weight:650;text-align:left;white-space:nowrap}}
    section[data-testid=stSidebar] [data-testid=stButton] button:hover{{color:{t['ink']};background:{t['card']};border-color:{t['edge']};transform:translateX(2px)}}
    .brand{{font:800 1.25rem Manrope;color:{t['ink']};padding:.7rem .6rem 1.2rem}} .brand small{{display:block;color:{t['muted']};font:700 .58rem 'DM Sans';letter-spacing:.18em;margin-left:1.8rem}}
    .welcome,.feature-card,.panel,[data-testid=stMetric],div[data-testid=stVerticalBlockBorderWrapper]{{background:{t['card']};border:1px solid {t['edge']};border-radius:18px}}
    .welcome{{padding:1rem;color:{t['muted']};margin-bottom:1rem}}.welcome b{{display:block;color:{t['ink']};font-size:1.08rem;margin-top:.25rem}}
    .feature-card,.panel{{padding:1.25rem;box-shadow:0 10px 32px #00000012;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease}}
    .feature-card:hover{{transform:translateY(-3px);border-color:{t['primary']};box-shadow:0 16px 38px #00000022}}
    .eyebrow{{font-size:.68rem;letter-spacing:.16em;font-weight:800;color:{t['primary']};margin:.55rem 0 .8rem}}
    .hero{{padding:7vh 2vw}}.hero h1{{font-size:clamp(2.7rem,5vw,4.6rem)!important;line-height:1.02}}.hero h1 span{{color:{t['primary']}}}.hero p,.feature-card p{{color:{t['muted']};line-height:1.7;font-size:1.08rem}}
    [data-testid=stForm]{{background:{t['surface']};border:1px solid {t['edge']};border-radius:18px;padding:1.2rem;box-shadow:0 15px 40px #00000014}}
    .stButton>button,[data-testid=stFormSubmitButton] button,[data-testid=stDownloadButton] button{{min-height:2.85rem;padding:.6rem 1rem;border-radius:999px;border:1px solid {t['edge']};background:{t['surface']};color:{t['ink']};font-size:calc(1rem * {scale/100:.2f});font-weight:700;transition:all .16s ease;white-space:normal}}
    .stButton>button:hover,[data-testid=stDownloadButton] button:hover{{border-color:{t['primary']};color:{t['primary']};transform:translateY(-1px);box-shadow:0 8px 22px #00000018}}
    [data-testid=stFormSubmitButton] button{{background:{t['primary']};border-color:{t['primary']};color:{'#003915' if dark else '#ffffff'};font-weight:800}}
    [data-testid=stMetric]{{padding:1.15rem;box-shadow:0 8px 24px #00000010;overflow:hidden}}[data-testid=stMetricLabel]{{color:{t['muted']}!important;font-weight:650;font-size:.76rem!important;letter-spacing:.09em;text-transform:uppercase}}[data-testid=stMetricValue]{{color:{t['ink']}!important;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:clamp(1.45rem,2.1vw,2.2rem)!important;line-height:1.12;white-space:nowrap}}[data-testid=stMetricDelta]{{font-size:.82rem!important}}
    .stTextInput input,.stNumberInput input,.stTextArea textarea,.stSelectbox>div>div,.stDateInput input{{background:{t['surface']}!important;border-color:{t['edge']}!important;color:{t['ink']}!important;border-radius:12px;min-height:2.8rem}}
    .stTextInput input:focus,.stNumberInput input:focus,.stTextArea textarea:focus{{border-color:{t['secondary']}!important;box-shadow:0 0 0 3px {t['secondary']}33!important}}
    [data-testid=stFileUploader]{{background:{t['surface']};border:1px dashed {t['edge']};border-radius:16px;padding:.65rem}}
    [data-testid=stDataFrame]{{border:1px solid {t['edge']};border-radius:14px;overflow:hidden}}
    .stTabs [data-baseweb=tab-list]{{gap:.5rem;border-bottom:1px solid {t['edge']};flex-wrap:wrap}}.stTabs [data-baseweb=tab]{{border-radius:10px 10px 0 0;padding:.65rem .85rem;font-weight:700;font-size:.92rem}}
    .stTabs [aria-selected=true]{{color:{t['primary']}!important;border-bottom-color:{t['primary']}!important}}
    .stAlert{{border-radius:14px}}[data-testid=stExpander]{{border:1px solid {t['edge']};border-radius:14px;background:{t['surface']}}}
    [data-testid=stCaptionContainer]{{color:{t['muted']}}} hr{{border-color:{t['edge']}}}
    @media(prefers-reduced-motion:reduce){{*,*::before,*::after{{transition:none!important;animation:none!important;scroll-behavior:auto!important}}}}
    @media(max-width:800px){{.block-container{{padding:1.2rem 1rem 3rem}}.hero{{padding:3vh 1vw}}.hero h1{{font-size:2.5rem!important}}}}
    {mode_css}
    </style>''',unsafe_allow_html=True)
