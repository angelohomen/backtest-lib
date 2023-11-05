import pandas as pd
from datetime import datetime
from src.utils.Log import Log
from src.indicators.MovingAverage import MovingAverage
from src.data_analysis.DataManipulation import DataManipulation

class AveragesCross():
    def __init__(
            self,
            slow_ma_inputs:dict,
            fast_ma_inputs:dict) -> None:
        self.__dm=DataManipulation()
        self.__signal=None
        self.__slow_ma_inputs=slow_ma_inputs
        self.__fast_ma_inputs=fast_ma_inputs

    def set_full_history(self, full_history):
        self.initialize_indicators(full_history)

    def initialize_indicators(self,full_history):
        self.__slow_ma_buff=MovingAverage(full_history,self.__slow_ma_inputs)
        self.__slow_ma=self.__slow_ma_buff.get_ma()
        self.__fast_ma_buff=MovingAverage(full_history,self.__fast_ma_inputs)
        self.__fast_ma=self.__fast_ma_buff.get_ma()

    def get_movings_averages(self):
        return {
            'fast': self.__fast_ma_buff,
            'slow': self.__slow_ma_buff
        }

    def trade_logic(self, history, step) -> int:
        if len(history)<2:
            return 0
        self.__curr_fast = self.__fast_ma[step-1]
        self.__curr_slow = self.__slow_ma[step-1]
        buy_signal=self.__curr_fast>self.__curr_slow
        sell_signal=self.__curr_fast<self.__curr_slow
        self.__signal=1 if buy_signal else -1 if sell_signal else 0
        return self.__signal
    
    def get_current_ma_values(self):
        return {
            'fast': self.__curr_fast,
            'slow': self.__curr_slow
        }