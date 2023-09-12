import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datacyclist.utils import plot_frame



class FastestSegment():
    """
    This class finds the segment in any ride that took the least time
    """
    def __init__(self, data, km):
        self.data = data
        self.km = km
        self._check_data()
        
        
    def _check_data(self):
        diff = {'activity_no', 'distance', 'time_diff', 'activity_distance', 
                'time_elapsed', 'distance_covered', 'year', 'month'} - set(self.data.columns)
        if len(list(diff)) > 0:
            raise KeyError(f'These columns are missing in the data: {list(diff)}')
        
    
    def find_window(self):
        
        fastest_time = 100000000000000000000
        time_start = 0
        time_end = 0
        activity_no = 0
        
        for activity in self.data['activity_no'].unique():
            
            act_data = self.data[self.data['activity_no'] == activity].copy()
            
            new_activity = False
            
            if act_data['distance'].sum() < self.km:
                continue
                
            else:
        
                for i, row in act_data.iterrows():
                    if new_activity:
                        break
                    start = i
                    time_start = row['time_elapsed']
                    if self.km <= row['distance'] <= self.km * 1.1:
                        time_diff = row['time_diff']

                        if time_diff < fastest_time:
                            fastest_time = time_diff
                            activity_no = row['activity_no']
                            time_end = time_start + time_diff
                        continue
                        
                    if row['activity_distance'] - row['distance_covered'] < self.km:
                        new_activity = True
                        continue
                        
                    sec_data = act_data[(row['distance_covered'] + self.km <= act_data['distance_covered']) & 
                                        (act_data['distance_covered'] <= row['distance_covered'] + self.km * 1.01)]
                    
                    time_diff = sec_data['time_elapsed'].min() - time_start
                    
                    if time_diff < fastest_time:
                        fastest_time = time_diff
                        activity_no = row['activity_no']
                        time_end = sec_data['time_elapsed'].min()
        
        return fastest_time, time_start, time_end, activity_no
    
    @staticmethod
    def _best_by(x, self):
        best_time, _, _, best = self.find_window()
        if best_time == 100000000000000000000:
            best_time = np.nan
            best = np.nan
        return best_time, best


    def top_rides(self, n=10):
        dates = self.data[['activity_no', 'year', 'month']].drop_duplicates()
        res = self.data.groupby('activity_no').apply(self._best_by, self).reset_index()
        res[['time', 'activity_no']] = pd.DataFrame(res[0].tolist(), index=res.index)
        del res[0]
        res = res.dropna().sort_values(by='time').reset_index(drop=True)
        res['activity_no'] = res['activity_no'].astype(int)
        res['time'] = res['time'].astype(int)
        res = pd.merge(res, dates, on='activity_no', how='left')

        by_month = res.groupby(['year', 'month'], as_index=False)['time'].min()
        by_month = pd.merge(by_month, res, on=['year', 'month', 'time'], how='left')
        by_month = by_month.sort_values(by=['activity_no']).reset_index(drop=True)
        
        self.top10 = res.head(n)
        self.by_month = by_month

        return self.top10, self.by_month


    def plot_best_rides(self):
        if hasattr(self, 'top10') and hasattr(self, 'by_month'):
            fig, ax = plt.subplots(1, 2, figsize=(15, 6), facecolor='#292525')
            fig.suptitle(f'Best rides of {int(self.km/1000)} Km', fontsize=18, color='w')
            (self.top10.sort_values(by='activity_no').set_index(['year', 'month'])['time'] / 3600).plot(ax=ax[0], color='#46a832')
            (self.by_month.set_index(['year', 'month'])['time'] / 3600).plot(ax=ax[1], color='#a86b32')
            ax[0] = plot_frame(ax[0])
            ax[1] = plot_frame(ax[1])
            ax[0].set_xlabel('')
            ax[1].set_xlabel('')
            ax[0].set_title('Top 10 rides', color='w', fontsize=14)
            ax[1].set_title('Best ride by month', color='w', fontsize=14)
            plt.show()
        else:
            _, _ = self.top_rides()
            self.plot_best_rides()