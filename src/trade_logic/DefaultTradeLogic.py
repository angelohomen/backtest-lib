import pandas as pd
from src.utils.Log import Log
from src.models.Trade import Trade
from src.data_analysis.DataManipulation import DataManipulation

class DefaultTradeLogic():
    @staticmethod
    def INPUTS_DEFAULT_LOGIC(
        input1:any=None,
        input2:any=None
    ):
        return {
            'input1': input1,
            'input2': input2
        }
    
    def __init__(
        self,
        qty: float,
        ENUM_TAKE_STOP_CALC_TYPE: str=Trade.ENUM_TAKE_STOP_CALC_TYPE_PTS,
        stop_loss: float=0,
        take_profit: float=0,
        INPUTS: dict=INPUTS_DEFAULT_LOGIC
        ):
        '''
            "DefaultTradeLogic()" is a class with all algo logics to trade, called by backtest. Do not delete set_full_history, update, trade_logic, close_trade_logic or modify_logic functions.
            When you don't need these, its just return a default value like False or 0.
            --------------------------------------------------------------------------
                Parameters
                    qty -> float:
                        Order quantity.
                    ENUM_TAKE_STOP_CALC_TYPE -> str (optional):
                        Take/Stop price calculation type.
                    stop_loss -> float (optional):
                        Order stop price.
                    take_profit -> float (optional):
                        Order stop price.
                    INPUTS -> object (optional):
                        Contains all trade logic inputs.

        '''
        self.__history=None
        self.qty=abs(qty)
        self.stop_loss=abs(stop_loss)
        self.take_profit=abs(take_profit)
        self.take_stop_calc=ENUM_TAKE_STOP_CALC_TYPE
        self.new_sl=0
        self.new_tp=0
        self.__trade:Trade=None
        self.__signal=None
        self.__dm=DataManipulation()

    def set_full_history(self, full_history):
        self.__full_history=full_history
        self.initialize_trades_logic()

    def initialize_trades_logic(self):
        # Set trading_strategies instance with inputs
        pass

    def update(self, history,trade):
        self.__history=history
        self.__trade=trade
        self.__time=pd.to_datetime(self.__history[-1][self.__dm.get_data_idx('time')])

    def trade_logic(self, step) -> int:
        # Call trading_strategies trade_logic
        
        
        buy_signal=False
        sell_signal=False

        self.__signal=1 if buy_signal else -1 if sell_signal else 0

        return self.__signal

    def close_trade_logic(self):
        return False

    def modify_logic(self) -> dict:
        return False