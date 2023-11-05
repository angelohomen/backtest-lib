from datetime import datetime, timedelta
from src.utils.Log import Log
from src.models.Trade import Trade
from src.Backtest import Backtest
import numpy as np
import pandas as pd

# Import new indicators
from src.indicators.MovingAverage import MovingAverage

class OptimizeOptions:
    @staticmethod
    def backtest_timeframe():
        return Backtest.OPT_ENUM_TIMEFRAME()
    
    @staticmethod
    def float(init_value, final_value, step):
        if final_value<=init_value:
            Log.LogMsg(Log.ENUM_MSG_TYPE_ERROR, 'Inputs error, final_value must be bigger than init_value.', datetime.now())
            raise Exception()
        return list(np.arange(init_value, final_value, step))
    
    @staticmethod
    def int(init_value, final_value, step):
        if final_value<=init_value:
            Log.LogMsg(Log.ENUM_MSG_TYPE_ERROR, 'Inputs error, final_value must be bigger than init_value.', datetime.now())
            raise Exception()
        return list(range(init_value, final_value, step))
    
    @staticmethod
    def take_stop_calc_type():
        return Trade.OPT_ENUM_TAKE_STOP_CALC_TYPE()
    
    @staticmethod
    def moving_average_calc_type():
        return MovingAverage.OPT_ENUMS_AVERAGE_TYPE()
    
    @staticmethod
    def time(init_value:datetime, final_value:datetime, step:int):
        to_return=[init_value]
        if final_value<=init_value:
            Log.LogMsg(Log.ENUM_MSG_TYPE_ERROR, 'Inputs error, final_value must be bigger than init_value.', datetime.now())
            raise Exception()
        return list(map(lambda x: x.time().strftime('%H:%M:%S'), pd.date_range(start=init_value, end = final_value, freq=timedelta(seconds=step))))