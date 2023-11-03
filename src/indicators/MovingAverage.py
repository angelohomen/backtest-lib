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
        self.__df = pd.DataFrame(history, columns=DataManipulation.PRICE_COLUMNS)
        if ENUM_AVERAGE_TYPE==self.ENUM_AVERAGE_TYPE_SMA:
            self.__df['ma'] = self.__df['close'].rolling(window=period).mean()
        else:
            self.__df['ma'] = self.__df['close'].ewm(span=period, min_periods=period, adjust=False).mean()

    def get_ma(self):
        return self.__df['ma'].values