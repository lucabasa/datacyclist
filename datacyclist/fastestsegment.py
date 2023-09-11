import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



class FastestSegment():
    def __init__(self):
        pass
    
    def find_window(self, data, km):
        
        fastest_time = 100000000000000000000
        time_start = 0
        time_end = 2
        activity_no = 0
        
        for activity in data['activity_no'].unique():
            
            act_data = data[data['activity_no'] == activity].copy()
            
            if act_data['distance'].sum() < km:
                continue
                
            else:
        
                for i, row in act_data.iterrows():
                    start = i
                    time_start = row['time_elapsed']
                    if km <= row['distance'] <= km * 1.1:

                        time_diff = row['time_diff']

                        if time_diff < fastest_time:
                            fastest_time = time_diff
                            activity_no = row['activity_no']
                        continue
                        
                    if row['activity_distance'] - row['distance_covered'] < km:
                        continue
                        
                    sec_data = act_data[(row['distance_covered'] + km < act_data['distance_covered']) & 
                                        (act_data['distance_covered'] <= row['distance_covered'] + km * 1.01)]
                    
                    time_diff = sec_data['time_elapsed'].min() - time_start
                    
                    if time_diff < fastest_time:
                        fastest_time = time_diff
                        activity_no = row['activity_no']
        
        return fastest_time, time_start, time_end, activity_no
    
    
def best_by(data, km):
    segment = FastestSegment()
    best_time, _, _, best = segment.find_window(data, km)
    if best_time == 100000000000000000000:
        best_time = np.nan
        best = np.nan
    return best_time, best


def top_rides(data, km):
    dates = data[['activity_no', 'year', 'month']].drop_duplicates()
    res = data.groupby('activity_no').apply(best_by, km).reset_index()
    res[['time', 'activity_no']] = pd.DataFrame(res[0].tolist(), index=res.index)
    del res[0]
    res = res.dropna().sort_values(by='time').reset_index(drop=True)
    res['activity_no'] = res['activity_no'].astype(int)
    res['time'] = res['time'].astype(int)
    res = pd.merge(res, dates, on='activity_no', how='left')
    
    by_month = res.groupby(['year', 'month'], as_index=False)['time'].min()
    by_month = pd.merge(by_month, res, on=['year', 'month', 'time'], how='left')
    by_month = by_month.sort_values(by=['activity_no']).reset_index(drop=True)
    
    return res.head(10), by_month


def plot_best_rides(top10, monthly, km):
    fig, ax = plt.subplots(1, 2, figsize=(15, 6), facecolor='#292525')
    fig.suptitle(f'Best rides of {int(km/1000)} Km', fontsize=18, color='w')
    (top10.sort_values(by='activity_no').set_index(['year', 'month'])['time'] / 3600).plot(ax=ax[0], color='#46a832')
    (monthly.set_index(['year', 'month'])['time'] / 3600).plot(ax=ax[1], color='#a86b32')
    ax[0] = plot_frame(ax[0])
    ax[1] = plot_frame(ax[1])
    ax[0].set_xlabel('')
    ax[1].set_xlabel('')
    ax[0].set_title('Top 10 rides', color='w', fontsize=14)
    ax[1].set_title('Best ride by month', color='w', fontsize=14)
    plt.show()