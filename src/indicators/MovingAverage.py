import pandas as pd
from datetime import datetime
from src.utils.Log import Log
from src.data_analysis.DataManipulation import DataManipulation

class MovingAverage():
    ENUM_AVERAGE_TYPE_SMA='SMA'
    ENUM_AVERAGE_TYPE_EMA='EMA'
    
    @staticmethod
    def INPUTS(
        ENUM_AVERAGE_TYPE:str=ENUM_AVERAGE_TYPE_SMA,
        period:int=9
    ):
        return {
            'ENUM_AVERAGE_TYPE': ENUM_AVERAGE_TYPE,
            'period': period
        }
    
    @staticmethod
    def OPT_ENUMS_AVERAGE_TYPE():
        return [MovingAverage.ENUM_AVERAGE_TYPE_SMA,MovingAverage.ENUM_AVERAGE_TYPE_EMA]

    def __init__(
        self,
        history,
        INPUTS:dict,
        logger: Log=None
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
        self.__INPUTS=INPUTS
        try:
            self.__df = pd.DataFrame(history, columns=DataManipulation.PRICE_COLUMNS)
            if self.__INPUTS['ENUM_AVERAGE_TYPE']==self.ENUM_AVERAGE_TYPE_SMA:
                self.__df['ma'] = self.__df['close'].rolling(window=self.__INPUTS['period']).mean()
                if logger: logger.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Moving average ({self.__INPUTS["period"]}) loaded.',time=datetime.now())
            elif self.__INPUTS['ENUM_AVERAGE_TYPE']==self.ENUM_AVERAGE_TYPE_EMA:
                self.__df['ma'] = self.__df['close'].ewm(span=self.__INPUTS['period'], min_periods=self.__INPUTS['period'], adjust=False).mean()
                if logger: logger.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Moving average ({self.__INPUTS["period"]}) loaded.',time=datetime.now())
            else:
                if logger: logger.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_ERROR,msg=f'ENUM_AVERAGE_TYPE ({self.__INPUTS["ENUM_AVERAGE_TYPE"]}) does not exist.',time=datetime.now())
                self.__df['ma']=float('NaN')
        except Exception as error:
            if logger: logger.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_ERROR,msg=error,time=datetime.now())

    def get_current_inputs(self):
        return {
            'ENUM_AVERAGE_TYPE':self.__INPUTS['ENUM_AVERAGE_TYPE'],
            'period':self.__INPUTS['period']
        }

    def get_ma(self):
        return self.__df['ma'].values