import datacyclist as dtc
import pandas as pd
import numpy as np
import pytest


def create_data():
    df = pd.DataFrame({'timestamp': [1, 2, 5], 
                       'activity_no': [3, 2, 1], 
                       'distance': [1,1,1], 
                       'time_elapsed': [1, 2, 3],
                       'time_diff': [0,1,2],
                       'activity_distance': [1,2,3], 
                       'distance_covered': [2,3,4], 
                       'year': [0,2,1], 
                       'month': [2,4,5] })
    return df

df = create_data()


@pytest.mark.parametrize("col", ['activity_no', 'distance', 'time_diff', 'activity_distance', 
                'time_elapsed', 'distance_covered', 'year', 'month'])
def test_missing_columns(col):
    """
    Test if a KeyError is raised if any of the required columns is missing
    """
    data = df.copy()
    del data[col]
    with pytest.raises(KeyError):
        pc = dtc.PowerCurve()
        pc.calculate_curve(data)


def test_toprides_io():
    fs = dtc.FastestSegment(df, 1)
    top10, monthly = fs.top_rides()
    diff = {'time', 'activity_no', 'year', 'month'} - set(top10.columns)
    assert len(list(diff)) == 0
    #assert res.shape[0] == 14
