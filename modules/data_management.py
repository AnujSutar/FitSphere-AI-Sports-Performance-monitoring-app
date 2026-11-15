import io
import pandas as pd
import streamlit as st
from pathlib import Path

def data_page():
    st.markdown("<div class='eyebrow'>DATA STUDIO · IMPORT & QUALITY</div><h1>Inspect and prepare datasets</h1>",unsafe_allow_html=True)
    st.caption('Preview, validate and export a copy. Uploaded data never overwrites application records.')
    uploaded=st.file_uploader('Upload CSV or Excel workbook',type=['csv','xlsx'])
    if uploaded:
        try:
            df=pd.read_csv(uploaded) if uploaded.name.lower().endswith('.csv') else pd.read_excel(uploaded)
            if df.empty: st.warning('This file has column headers but no data rows.')
            else:
                a,b,c=st.columns(3); a.metric('Rows',f'{len(df):,}'); b.metric('Columns',len(df.columns)); c.metric('Duplicate rows',int(df.duplicated().sum()))
                st.subheader('Preview'); st.dataframe(df.head(50),hide_index=True,use_container_width=True)
                quality=pd.DataFrame({'Column':df.columns,'Missing':df.isna().sum().values,'Type':[str(t) for t in df.dtypes],'Unique values':[df[c].nunique(dropna=True) for c in df.columns]})
                st.subheader('Data quality'); st.dataframe(quality,hide_index=True,use_container_width=True)
                if df.duplicated().any(): st.warning(f'{int(df.duplicated().sum())} duplicate row(s) detected. Export removes duplicates.')
                left,right=st.columns(2)
                left.download_button('Download cleaned CSV',df.drop_duplicates().to_csv(index=False).encode('utf-8'),file_name='dataset_cleaned.csv',mime='text/csv',use_container_width=True)
                buf=io.BytesIO()
                with pd.ExcelWriter(buf,engine='openpyxl') as writer:
                    df.drop_duplicates().to_excel(writer,index=False,sheet_name='Cleaned data')
                    quality.to_excel(writer,index=False,sheet_name='Quality report')
                right.download_button('Download Excel report',buf.getvalue(),file_name='dataset_quality_report.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
        except Exception as e: st.error(f'Could not read this file. Check that it is a valid CSV/XLSX workbook. Details: {e}')
    st.divider(); st.subheader('Built-in demo datasets')
    root=Path(__file__).resolve().parents[1]
    for filename,label in [('sample_players.csv','Synthetic football player sample'),('sample_multisport.csv','Synthetic multi-sport sample')]:
        path=root/'data'/filename
        if path.exists():
            sample=pd.read_csv(path); st.markdown(f'**{label}** · {len(sample)} records'); st.dataframe(sample.head(12),hide_index=True,use_container_width=True); st.download_button(f'Download {label} CSV',sample.to_csv(index=False).encode(),file_name=filename,mime='text/csv',key=f'dl_{filename}')
    players=pd.read_csv(root/'data'/'sample_players.csv'); buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine='openpyxl') as writer: players.head(0).to_excel(writer,index=False,sheet_name='Player template')
    st.download_button('Download player import template (Excel)',buf.getvalue(),file_name='player_import_template.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
