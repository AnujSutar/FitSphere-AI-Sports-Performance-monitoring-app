from pathlib import Path
import io
import pandas as pd
from modules.athlete_dashboard import load
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score

def predict_value(frame, features=None):
    features=features or ['age','position','appearances','goals','assists','minutes']
    numeric=[x for x in features if x!='position']
    prep=ColumnTransformer([('num',SimpleImputer(strategy='median'),numeric),('cat',OneHotEncoder(handle_unknown='ignore'),['position'])])
    xtr,xte,ytr,yte=train_test_split(frame[features],frame.market_value_m,test_size=.25,random_state=42)
    pipe=Pipeline([('pre',prep),('model',RandomForestRegressor(n_estimators=40,max_depth=5,random_state=42))]).fit(xtr,ytr)
    pred=pipe.predict(xte)
    return pipe,{'MAE':mean_absolute_error(yte,pred),'RMSE':mean_squared_error(yte,pred)**.5,'R2':r2_score(yte,pred)}

if __name__=='__main__':
    df=load(); pipe,metrics=predict_value(df); print('valuation holdout metrics',metrics)
    print('sample prediction',pipe.predict(df[['age','position','appearances','goals','assists','minutes']].iloc[:1])[0])
    out=io.BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as w: df.to_excel(w,index=False)
    assert pd.read_excel(io.BytesIO(out.getvalue())).equals(df)
    print('excel round trip ok')
