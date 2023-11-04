import pandas as pd
from datetime import datetime
from src.utils.Log import Log
from src.data_analysis.DataManipulation import DataManipulation

class MovingAverage():
    ENUM_AVERAGE_TYPE_SMA='SMA'
    ENUM_AVERAGE_TYPE_EMA='EMA'
    def __init__(
        self,
        history,
        ENUM_AVERAGE_TYPE,
        period:int,
        log:bool=False
        ):
        '''
            "Moving Average()" class to generate Moving Averages to a price dataframe.
            --------------------------------------------------------------------------
                Parameters
                    history -> pandas.DataFrame():
                        Dataframe generated at src.data_analysis.DataManipulation with DataManipulation.PRICE_COLUMNS header.
                    ENUM_AVERAGE_TYPE -> MovingAverage.ENUM_AVERAGE_TYPE:
                        Calculation type for the moving average (simple or exponential).
                    period -> int:
                        Number of periods.
                    log -> bool (optional):
                        Set True if want to retrieve bot logs.
        '''
        self.__log=log
        self.__df = pd.DataFrame(history, columns=DataManipulation.PRICE_COLUMNS)
        if ENUM_AVERAGE_TYPE==self.ENUM_AVERAGE_TYPE_SMA:
            self.__df['ma'] = self.__df['close'].rolling(window=period).mean()
        elif ENUM_AVERAGE_TYPE==self.ENUM_AVERAGE_TYPE_EMA:
            self.__df['ma'] = self.__df['close'].ewm(span=period, min_periods=period, adjust=False).mean()
        else:
            if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_ERROR,msg='ENUM_AVERAGE_TYPE ({ENUM_AVERAGE_TYPE}) does not exist.',time=datetime.now())
            self.__df['ma']=float('NaN')

    def get_ma(self):
        return self.__df['ma'].values