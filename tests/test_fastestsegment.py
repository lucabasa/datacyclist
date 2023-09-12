import datacyclist as dtc
import pandas as pd
import numpy as np
import pytest


def create_data():
    df = pd.DataFrame({'activity_no': [1, 1, 1, 1, 1, 1], 
                       'distance': [0,5,5, 5, 5, 1], 
                       'time_elapsed': [0, 1, 2, 3, 4, 5],
                       'time_diff': [1,1,1, 1, 1, 1],
                       'activity_distance': [21]*6, 
                       'distance_covered': [0,5,10,15,20,21], 
                       'year': [1,1,1, 1, 1, 1], 
                       'month': [1,1,1 ,1, 1, 1] })
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
    diff = {'time', 'activity_no', 'year', 'month'} - set(monthly.columns)
    assert len(list(diff)) == 0
    

def test_findwindow():
    fs = dtc.FastestSegment(df, 20)
    fastest_time, time_start, time_end, activity_no = fs.find_window()
    assert fastest_time == 4
    assert time_start == 1
    assert time_end == 4  
    assert activity_no == 1
    
