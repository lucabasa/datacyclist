import datacyclist as dtc
import pandas as pd
import numpy as np
import pytest


def create_data():
    df = pd.DataFrame({'timestamp': [1, np.nan, 5], 
                       'activity_no': [3, 2, 1], 
                       'distance': [1,1,1], 
                       'time_elapsed': [1, 2, 3], 
                       'activity_distance': [1,2,3], 
                       'distance_covered': [2,3,4], 
                       'year': [0,2,1], 
                       'month': [2,4,5] })
    return df

df = create_data()


def test_fastestsegment():
    pass
