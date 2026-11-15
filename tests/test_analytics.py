from pathlib import Path
import pandas as pd

def test_demo_dataset_valid():
    df=pd.read_csv(Path(__file__).parents[1]/'data'/'sample_players.csv')
    assert len(df)>=10
    assert {'name','age','position','minutes','market_value_m'} <= set(df.columns)
    assert (df.market_value_m>=0).all()
