import pandas as pd
from src.utils.Log import Log
from src.utils.TimeToTrade import TimeToTrade
from src.models.Trade import Trade
from src.indicators.MovingAverage import MovingAverage
from src.data_analysis.DataManipulation import DataManipulation

# Import trade_logics
from src.trading_strategies.averages_cross import AveragesCross

class TradeLogic():
    @staticmethod
    def INPUTS(
        trading_time: TimeToTrade=TimeToTrade('09:00:00', '16:00:00', '17:00:00')
    ):
        return {
            'trading_time': trading_time
        }

    def __init__(
        self,
        qty: float,
        ENUM_TAKE_STOP_CALC_TYPE: str=Trade.ENUM_TAKE_STOP_CALC_TYPE_PTS,
        stop_loss: float=0,
        take_profit: float=0,
        INPUTS=INPUTS()
        ):
        '''
            "TradeLogic()" is a class with all algo logics to trade, called by backtest. Do not delete set_full_history, update, trade_logic, close_trade_logic or modify_logic functions.
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
        if not INPUTS: self.INPUTS()
        self.__history=None
        self.qty=abs(qty)
        self.stop_loss=abs(stop_loss)
        self.take_profit=abs(take_profit)
        self.take_stop_calc=ENUM_TAKE_STOP_CALC_TYPE
        self.new_sl=0
        self.new_tp=0
        self.__signal=None
        self.__dm=DataManipulation()
        self.__INPUTS=INPUTS
        self.__time_trade=self.__INPUTS['trading_time']
        self.__logger=None

        # indicators inputs
        

    def set_log_pointer(self,log:Log):
        self.__logger=log

    def get_current_inputs(self):
        return ({
            'qty': self.qty,
            'ENUM_TAKE_STOP_CALC_TYPE': self.take_stop_calc,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        }|{
            f'{k}': v for k, v in self.__time_trade.get_current_inputs().items()
        })

    def set_full_history(self, full_history):
        self.__full_history=full_history
        self.initialize_trades_logic()

    def initialize_trades_logic(self):
        # Set trading_strategies instance with inputs
        pass

    def update(self, history,trades):
        self.__history=history
        self.__time=pd.to_datetime(self.__history[-1][self.__dm.get_data_idx('time')])

    def trade_logic(self, step) -> int:
        # Check if is time to trade
        if not self.__time_to_trade():
            return 0
        if len(self.__history)<2:
            return 0
        curr_close_price = self.__history[-2][self.__dm.get_data_idx('close')]

        # Call trading_strategies trade_logic
        

        buy_signal=False
        sell_signal=False

        self.__signal=1 if buy_signal else -1 if sell_signal else 0

        return self.__signal
    
    def __time_to_trade(self):
        if self.__time_trade:
            return self.__time_trade.TimeToOpenTrades(self.__time)
        return True

    def close_trade_logic(self,__curr_trade):
        # Inverse signal
        if self.__inverse_signal_close_trade(__curr_trade):
            return True
        # Time to close positions
        if self.__time_to_close(__curr_trade):
            return True

        return False
    
    def __time_to_close(self,__trade):
        if self.__time_trade:
            if self.__time_trade.TimeToCloseTrades(self.__time):
                if self.__logger: self.__logger.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Close trade ({__trade.get_trade_info()["trade_id"]}) due to time.',time=self.__time)
                return True
        return False
    
    def __inverse_signal_close_trade(self,__trade):
        if __trade:
            if self.__signal == 1:
                if __trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if __trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                        if self.__logger: self.__logger.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Close trade ({__trade.get_trade_info()["trade_id"]}) logic due to inverse signal.',time=self.__time)
                        return True
            if self.__signal == -1:
                if __trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if __trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                        if self.__logger: self.__logger.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Close trade ({__trade.get_trade_info()["trade_id"]}) logic due to inverse signal.',time=self.__time)
                        return True
        return False

    def modify_logic(self,__trade) -> dict:
        if len(self.__history)<2:
            return False
        curr_close_price = self.__history[-2][self.__dm.get_data_idx('close')]
        if self.__signal==0:
            return False
        if self.__signal==1:
            if __trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                update=False
                new_sl=__trade.calculate_take_stop(curr_close_price, self.stop_loss, False, True)
                new_tp=__trade.calculate_take_stop(curr_close_price, self.take_profit, True, True)
                if __trade.get_stop_price()<new_sl and new_sl>0:
                    self.new_sl=new_sl
                    update=True
                if __trade.get_take_price()>new_tp and new_tp>0:
                    self.new_tp=new_tp
                    update=True
                return update
        if self.__signal==-1:
            if __trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                update=False
                new_sl=__trade.calculate_take_stop(curr_close_price, self.stop_loss, False, False)
                new_tp=__trade.calculate_take_stop(curr_close_price, self.take_profit, True, False)
                if __trade.get_stop_price()>new_sl and new_sl>0:
                    self.new_sl=new_sl
                    update=True
                if __trade.get_take_price()<new_tp and new_tp>0:
                    self.new_tp=new_tp
                    update=True
                return update
        return False
    
    def optimize_possibilities(
        self,
        stop_loss=[],
        take_profit=[],
        time_to_open_trades=[],
        time_to_stop_open=[],
        time_to_close_trades=[]
    ):
        stop_loss=stop_loss if len(stop_loss)>0 else [self.stop_loss]
        take_profit=take_profit if len(take_profit)>0 else [self.take_profit]
        time_to_open_trades=time_to_open_trades if len(time_to_open_trades)>0 else [self.__time_trade.time_to_open_trades]
        time_to_stop_open=time_to_stop_open if len(time_to_stop_open)>0 else [self.__time_trade.time_to_stop_open]
        time_to_close_trades=time_to_close_trades if len(time_to_close_trades)>0 else [self.__time_trade.time_to_close_trades]

        return [
            TradeLogic(
                qty=self.qty, 
                ENUM_TAKE_STOP_CALC_TYPE=self.take_stop_calc, 
                stop_loss=sl, 
                take_profit=tp, 
                INPUTS=TradeLogic.INPUTS(
                    trading_time=TimeToTrade(tm_op, tm_stp, tm_cls)
                )
            )
            for sl in stop_loss for tp in take_profit for tm_op in time_to_open_trades for tm_stp in time_to_stop_open for tm_cls in time_to_close_trades
        ]