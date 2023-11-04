import pandas as pd
from datetime import datetime
import yfinance as yf
from dateutil.relativedelta import relativedelta
today = datetime.now()
import warnings
warnings.filterwarnings('ignore')
from src.data_analysis.MT5 import MetaTraderConnection

class DataManipulation():
    CALL_LETTERS = ['A','B','C','D','E','F','G','H','I','J','K','L']
    PUT_LETTERS = ['M','N','O','P','Q','R','S','T','U','V','W','X']
    PRICE_COLUMNS = ['time', 'open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']
    __TRANSLATE_MT5_TO_YFINANCE={
        'TIMEFRAME_M1': '1m',
        'TIMEFRAME_M2': '1m',
        'TIMEFRAME_M3': '1m',
        'TIMEFRAME_M4': '1m',
        'TIMEFRAME_M5': '5m',
        'TIMEFRAME_M6': '5m',
        'TIMEFRAME_M10': '5m',
        'TIMEFRAME_M12': '5m',
        'TIMEFRAME_M15': '15m',
        'TIMEFRAME_M20': '15m',
        'TIMEFRAME_M30': '15m',
        'TIMEFRAME_H1': '1h',
        'TIMEFRAME_H2': '1h',
        'TIMEFRAME_H3': '1h',
        'TIMEFRAME_H4': '1h',
        'TIMEFRAME_H6': '1h',
        'TIMEFRAME_H8': '1h',
        'TIMEFRAME_H12': '1h',
        'TIMEFRAME_D1': '1d',
        'TIMEFRAME_W1': '1d',
        'TIMEFRAME_MN1': '1mo',
        'TIMEFRAME_MN3': '3mo',
        'TIMEFRAME_MN6': '6mo',
        'TIMEFRAME_Y1': '1y',
        'TIMEFRAME_Y2': '2y',
        'TIMEFRAME_Y5': '5y',
        'TIMEFRAME_Y10': '10y',
    }
    def __init__(self):
        '''
            "DataManipulation()" is a class to search data from a ticker.
            --------------------------------------------------------------------------
                Parameters
                    None
        '''
        pass

    def get_symbol_ohlc_df(self, symbol: str, timeframe: str, count: int) -> pd.DataFrame():
        self.MT5 = MetaTraderConnection()
        self.MT5.get_symbol_select(symbol, True)
        if count > 676564 or count == -1:
            count = 676564
        raw_data = self.MT5.get_symbol_ohlc(symbol,timeframe,0,count)
        if raw_data is None:
            raw_data = yf.download(symbol, period=self.__TRANSLATE_MT5_TO_YFINANCE[timeframe], start='1900-01-01', end=today, progress=False)
            raw_data.reset_index(inplace=True)
            raw_data=raw_data[['Date', 'Open', 'High', 'Low', 'Adj Close', 'Volume']]
            raw_data['Spread']=0
            raw_data['RealVolume']=raw_data['Volume']
            raw_data.columns=self.PRICE_COLUMNS
            df = pd.DataFrame(raw_data)
        else:
            dict_list = [dict(list(zip(self.PRICE_COLUMNS,list(i)))) for i in list(raw_data)]
            df = pd.DataFrame(list(dict_list))
        try:
            df['time'] = pd.to_datetime(df['time'], unit = 's')
        except:
            df['time'] = pd.to_datetime(df['time'], errors="ignore")
        df=df.sort_values(by=['time'])
        df.reset_index(drop=True, inplace=True)
        df=df[df['time']>today - relativedelta(years=10)]
        return df
    
    def get_data_idx(self,data):
        return self.PRICE_COLUMNS.index(data)