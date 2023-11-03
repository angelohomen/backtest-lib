from src.data_analysis.DataManipulation import DataManipulation
import pandas as pd

class MovingAverage():
    ENUM_AVERAGE_TYPE_SMA='SMA'
    ENUM_AVERAGE_TYPE_EMA='EMA'
    def __init__(
        self,
        history,
        ENUM_AVERAGE_TYPE,
        period:int
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
        '''
        self.__df = pd.DataFrame(history, columns=DataManipulation.PRICE_COLUMNS)
        if ENUM_AVERAGE_TYPE==self.ENUM_AVERAGE_TYPE_SMA:
            self.__df['ma'] = self.__df['close'].rolling(window=period).mean()
        elif ENUM_AVERAGE_TYPE==self.ENUM_AVERAGE_TYPE_EMA:
            self.__df['ma'] = self.__df['close'].ewm(span=period, min_periods=period, adjust=False).mean()
        else:
            print(f'[WARNING] ENUM_AVERAGE_TYPE ({ENUM_AVERAGE_TYPE}) does not exist.')
            self.__df['ma']=float('NaN')

    def get_ma(self):
        return self.__df['ma'].values