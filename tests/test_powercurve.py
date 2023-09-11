import datacyclist as dtc
import pandas as pd
import numpy as np
import pytest


def create_data():
    df = pd.DataFrame({'timestamp': [1, np.nan, 5], 
                       'power': [3, 2, 1], 
                       'heart_rate': [1,1,1], 
                       'cadence': [1, 2, 3] })
    return df

df = create_data()

@pytest.mark.parametrize("col", ['timestamp', 'power', 'cadence', 'heart_rate'])
def test_missing_columns(col):
    data = df.copy()
    del data[col]
    with pytest.raises(KeyError):
        pc = dtc.PowerCurve()
        pc.calculate_curve(data)

