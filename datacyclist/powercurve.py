import pandas as pd
import numpy as np


class PowerDict(dict):
    def __init__(self):
        self.activity_best = 0
        self.activity_HR = 0
        self.activity_cadence = 0
        self.alltime_best = 0
        self.alltime_HR = 0
        self.alltime_cadence = 0
        
    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__[key] = value
        
        
        
class PowerCurve(object):
    def __init__(self):
        self.sec_list = [1,2,5,10,20,30,
                         60,120,300,600,1200,
                         3600,7200,18000]
        for sec in self.sec_list:
            setattr(self, f'sec_{sec}', PowerDict())
            
    def _rolling_avgs(self):
        for sec in [sec for sec in self.sec_list if sec < self.data['time_elapsed'].max()]:
            attr = getattr(self, f'sec_{sec}')
            attr['activity_best'] = 0
            attr['activity_HR'] = 0
            attr['activity_cadence'] = 0
            rolling_avg = self.data.rolling(f'{sec}s', min_periods=sec)['power'].mean()
            rolling_avg_hr = self.data.rolling(f'{sec}s')['heart_rate'].mean()  #todo: not good estimate (maybe with max)
            rolling_avg_cad = self.data.rolling(f'{sec}s')['cadence'].mean()
            attr['activity_best'] = rolling_avg.max()
            max_avg_power_timestamp = rolling_avg.idxmax()
            try:
                attr['activity_HR'] = rolling_avg_hr.loc[max_avg_power_timestamp]
                attr['activity_cadence'] = rolling_avg_cad.loc[max_avg_power_timestamp]
            except KeyError:
                attr['activity_HR'] = 0  # The error is triggered by missing power data or big time gaps
                attr['activity_cadence'] = 0
                #attr['activity_best'] = 0
            if attr['activity_best'] > attr['alltime_best']:
                attr['alltime_best'] = attr['activity_best']
                attr['alltime_HR'] = attr['activity_HR']
                attr['alltime_cadence'] = attr['activity_cadence']
                
    def _check_input(self, data):
        diff = {'timestamp', 'power', 'cadence', 'heart_rate'} - set(data.columns)
        if len(list(diff)) > 0:
            raise KeyError(f'These columns are missing in the data: {list(diff)}')
    
    def calculate_curve(self, activity_data):
        self._check_input(activity_data)
        self.data = activity_data.copy().set_index('timestamp')
        self.data = self.data.resample('1S').ffill()
        if self.data['power'].isna().all():
            for sec in self.sec_list:
                attr = getattr(self, f'sec_{sec}')
                attr['activity_best'] = 0
                attr['activity_HR'] = 0
                attr['activity_cadence'] = 0
        else:
            self.data = self.data.fillna(0)
            self._rolling_avgs()            

    def get_activity_curve(self):
        activity_curve = []
        best_curve = []
        hr_curve = []
        hr_best = []
        cad_curve = []
        cad_best = []
        for sec in self.sec_list:
            attr = getattr(self, f'sec_{sec}')
            activity_curve.append(attr['activity_best'])
            best_curve.append(attr['alltime_best'])
            hr_curve.append(attr['activity_HR'])
            hr_best.append(attr['alltime_HR'])
            cad_curve.append(attr['activity_cadence'])
            cad_best.append(attr['alltime_cadence'])
        
        res = pd.DataFrame({'Time': self.sec_list, 
                            'Activity Curve': activity_curve, 
                            'Best Curve': best_curve, 
                            'Activity HR': hr_curve, 
                            'HR Best Curve': hr_best, 
                            'Activity Cadence': cad_curve, 
                            'Cadence Best Curve': cad_best})
        return res
    
    
    def get_ftp(self, data):
        for sec in [1200, 3600]:
            attr = getattr(self, f'sec_{sec}')
            data[f'{int(sec / 60)}min_activity_power'] = np.where(attr['activity_best'] == 0, np.nan, attr['activity_best'])
            data[f'{int(sec / 60)}min_power'] = np.where(attr['alltime_best'] == 0, np.nan, attr['alltime_best'])
            data[f'{int(sec / 60)}min_activity_HR'] = np.where(attr['activity_HR'] == 0, np.nan, attr['activity_HR'])
            data[f'{int(sec / 60)}min_HR'] = np.where(attr['alltime_HR'] == 0, np.nan, attr['alltime_HR'])                      
        
        data['activity_FTP'] = np.where(data['60min_activity_power'].isna(), data['20min_activity_power'] * 0.95,
                                        np.where(data['20min_activity_power'] * 0.95 >= data['60min_activity_power'], 
                                        data['20min_activity_power'] * 0.95, data['60min_activity_power']))
        
        data['FTP'] = np.where(data['60min_power'].isna(), data['20min_power'] * 0.95,
                               np.where(data['20min_power'] * 0.95 >= data['60min_power'], 
                              data['20min_power'] * 0.95, data['60min_power']))
        
        data['FTP_change'] = np.where(data['FTP'] == data['activity_FTP'], 1, 0)
        
        data['Threshold_HR'] = np.where(data['FTP_change'] == 1, data['20min_activity_HR'], data['20min_HR'])
        
        del data['activity_FTP']
        
        return data
