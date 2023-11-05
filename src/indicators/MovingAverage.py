import pandas as pd
from datetime import datetime
from src.utils.Log import Log
from src.data_analysis.DataManipulation import DataManipulation

class MovingAverage():
    ENUM_AVERAGE_TYPE_SMA='SMA'
    ENUM_AVERAGE_TYPE_EMA='EMA'
    
    @staticmethod
    def INPUTS_MA(
        ENUM_AVERAGE_TYPE:str=ENUM_AVERAGE_TYPE_SMA,
        period:int=9
    ):
        return {
            'ENUM_AVERAGE_TYPE': ENUM_AVERAGE_TYPE,
            'period': period
        }

    def __init__(
        self,
        history,
        INPUTS_MA:dict
        ):
        '''
            "Moving Average()" class to generate Moving Averages to a price dataframe.
            --------------------------------------------------------------------------
                Parameters
                    history -> pandas.DataFrame():
                        Dataframe generated at src.data_analysis.DataManipulation with DataManipulation.PRICE_COLUMNS header.
                    INPUTS_MA dict, with keys:
                        ENUM_AVERAGE_TYPE -> MovingAverage.ENUM_AVERAGE_TYPE:
                            Calculation type for the moving average (simple or exponential).
                        period -> int:
                            Number of periods.
        '''
        try:
            self.__df = pd.DataFrame(history, columns=DataManipulation.PRICE_COLUMNS)
            if INPUTS_MA['ENUM_AVERAGE_TYPE']==self.ENUM_AVERAGE_TYPE_SMA:
                self.__df['ma'] = self.__df['close'].rolling(window=INPUTS_MA['period']).mean()
            elif INPUTS_MA['ENUM_AVERAGE_TYPE']==self.ENUM_AVERAGE_TYPE_EMA:
                self.__df['ma'] = self.__df['close'].ewm(span=INPUTS_MA['period'], min_periods=INPUTS_MA['period'], adjust=False).mean()
            else:
                Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_ERROR,msg=f'ENUM_AVERAGE_TYPE ({INPUTS_MA["ENUM_AVERAGE_TYPE"]}) does not exist.',time=datetime.now())
                self.__df['ma']=float('NaN')
        except Exception as error:
            Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_ERROR,msg=error,time=datetime.now())

    def get_ma(self):
        return self.__df['ma'].values