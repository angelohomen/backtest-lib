from iteration_utilities import unique_everseen
import pandas as pd
from datetime import datetime
from src.utils.Log import Log
from src.utils.TimeToTrade import TimeToTrade
from src.models.Trade import Trade
from src.indicators.MovingAverage import MovingAverage
from src.data_analysis.DataManipulation import DataManipulation

# Import trade_logics
from src.trading_strategies.averages_cross import AveragesCross

class AverageCrossLogic():
    @staticmethod
    def INPUTS_AC_LOGIC(
        fast_ma_inputs: dict=MovingAverage.INPUTS_MA(9),
        slow_ma_inputs: dict=MovingAverage.INPUTS_MA(20),
        trading_time: TimeToTrade=TimeToTrade('09:00:00', '16:00:00', '17:00:00')
    ):
        return {
            'fast_ma_inputs': fast_ma_inputs,
            'slow_ma_inputs': slow_ma_inputs,
            'trading_time': trading_time
        }

    def __init__(
        self,
        qty: float,
        ENUM_TAKE_STOP_CALC_TYPE: str=Trade.ENUM_TAKE_STOP_CALC_TYPE_PTS,
        stop_loss: float=0,
        take_profit: float=0,
        INPUTS=None
        ):
        '''
            "AverageCrossLogic()" is a class with all algo logics to trade, called by backtest. Do not delete set_full_history, update, trade_logic, close_trade_logic or modify_logic functions.
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
                    INPUTS -> dict (optional) with keys:
                        fast_ma_inputs -> MovingAverage.INPUTS_MA. Fast MA parameters.
                        slow_ma_inputs -> MovingAverage.INPUTS_MA. Slow MA parameters.
                        trading_time -> TimeToTrade. Valid to intraday backtesting, None to diary.

        '''
        if not INPUTS: self.INPUTS_AC_LOGIC()
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
        self.__INPUTS=INPUTS
        self.__time_trade=self.__INPUTS['trading_time']

        # indicators inputs
        self.__fast_ma_inputs=self.__INPUTS['fast_ma_inputs']
        self.__slow_ma_inputs=self.__INPUTS['slow_ma_inputs']

    def get_current_inputs(self):
        return ({
            'qty': self.qty,
            'ENUM_TAKE_STOP_CALC_TYPE': self.take_stop_calc,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        }|{
            f'fast_ma_{k}': v for k, v in self.__average_cross.get_movings_averages()['fast'].get_current_inputs().items()
        }|{
            f'slow_ma_{k}': v for k, v in self.__average_cross.get_movings_averages()['slow'].get_current_inputs().items()
        }|{
            f'{k}': v for k, v in self.__time_trade.get_current_inputs().items()
        })

    def set_full_history(self, full_history):
        self.__full_history=full_history
        self.initialize_trades_logic()

    def initialize_trades_logic(self):
        # Set trading_strategies instance with inputs
        self.__average_cross=AveragesCross(
            fast_ma_inputs=MovingAverage.INPUTS_MA(
                ENUM_AVERAGE_TYPE=self.__fast_ma_inputs['ENUM_AVERAGE_TYPE'],
                period=self.__fast_ma_inputs['period']
            ),
            slow_ma_inputs=MovingAverage.INPUTS_MA(
                ENUM_AVERAGE_TYPE=self.__slow_ma_inputs['ENUM_AVERAGE_TYPE'],
                period=self.__slow_ma_inputs['period']
            )
        )
        self.__average_cross.set_full_history(self.__full_history)

    def update(self, history,trade):
        self.__history=history
        self.__trade=trade
        self.__time=pd.to_datetime(self.__history[-1][self.__dm.get_data_idx('time')])

    def trade_logic(self, step) -> int:
        # Check if is time to trade
        if not self.__time_to_trade():
            return 0
        
        if len(self.__history)<2:
            return 0
        curr_close_price = self.__history[-2][self.__dm.get_data_idx('close')]

        # Call trading_strategies trade_logic
        average_cross_signal=self.__average_cross.trade_logic(self.__history,step)
        curr_ma=self.__average_cross.get_current_ma_values()

        buy_signal=average_cross_signal==1 and curr_close_price>curr_ma['fast']
        sell_signal=average_cross_signal==-1 and curr_close_price<curr_ma['fast']

        self.__signal=1 if buy_signal else -1 if sell_signal else 0

        return self.__signal
    
    def __time_to_trade(self):
        if self.__time_trade:
            return self.__time_trade.TimeToOpenTrades(self.__time)
        return True

    def close_trade_logic(self):
        # Inverse signal
        if self.__inverse_signal_close_trade():
            return True
        # Time to close positions
        if self.__time_to_close():
            return True

        return False
    
    def __time_to_close(self):
        if self.__time_trade:
            if self.__time_trade.TimeToCloseTrades(self.__time):
                Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Close trade ({self.__trade.get_trade_info()["trade_id"]}) due to time.',time=self.__time)
                return True
        return False
    
    def __inverse_signal_close_trade(self):
        if self.__trade:
            if self.__signal == 1:
                if self.__trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Close trade ({self.__trade.get_trade_info()["trade_id"]}) logic due to inverse signal.',time=self.__time)
                        return True
            if self.__signal == -1:
                if self.__trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                        Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Close trade ({self.__trade.get_trade_info()["trade_id"]}) logic due to inverse signal.',time=self.__time)
                        return True
        return False

    def modify_logic(self) -> dict:
        if len(self.__history)<2:
            return False
        curr_close_price = self.__history[-2][self.__dm.get_data_idx('close')]
        if self.__signal==0:
            return False
        if self.__signal==1:
            if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                update=False
                new_sl=self.__trade.calculate_take_stop(curr_close_price, self.stop_loss, False, True)
                new_tp=self.__trade.calculate_take_stop(curr_close_price, self.stop_loss, True, True)
                if self.__trade.get_stop_price()<new_sl and new_sl>0:
                    self.new_sl=new_sl
                    update=True
                if self.__trade.get_take_price()>new_tp and new_tp>0:
                    self.new_tp=new_tp
                    update=True
                return update
        if self.__signal==-1:
            if self.__trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                update=False
                new_sl=self.__trade.calculate_take_stop(curr_close_price, self.stop_loss, False, False)
                new_tp=self.__trade.calculate_take_stop(curr_close_price, self.stop_loss, True, False)
                if self.__trade.get_stop_price()>new_sl and new_sl>0:
                    self.new_sl=new_sl
                    update=True
                if self.__trade.get_take_price()<new_tp and new_tp>0:
                    self.new_tp=new_tp
                    update=True
                return update
        return False
    
    def optimize_possibilities(
        self,
        stop_loss=[],
        take_profit=[],
        slow_ma_calc_type=[],
        slow_ma_period=[],
        fast_ma_calc_type=[],
        fast_ma_period=[],
        time_to_open_trades=[],
        time_to_stop_open=[],
        time_to_close_trades=[]
    ):
        stop_loss=stop_loss if len(stop_loss)>0 else [self.stop_loss]
        take_profit=take_profit if len(take_profit)>0 else [self.take_profit]
        slow_ma_calc_type=slow_ma_calc_type if len(slow_ma_calc_type)>0 else [self.__slow_ma_inputs['ENUM_AVERAGE_TYPE']]
        slow_ma_period=slow_ma_period if len(slow_ma_period)>0 else [self.__slow_ma_inputs['period']]
        fast_ma_calc_type=fast_ma_calc_type if len(fast_ma_calc_type)>0 else [self.__fast_ma_inputs['ENUM_AVERAGE_TYPE']]
        fast_ma_period=fast_ma_period if len(fast_ma_period)>0 else [self.__fast_ma_inputs['period']]
        time_to_open_trades=time_to_open_trades if len(time_to_open_trades)>0 else [self.__time_trade.time_to_open_trades]
        time_to_stop_open=time_to_stop_open if len(time_to_stop_open)>0 else [self.__time_trade.time_to_stop_open]
        time_to_close_trades=time_to_close_trades if len(time_to_close_trades)>0 else [self.__time_trade.time_to_close_trades]

        return [
            AverageCrossLogic(
                qty=self.qty, 
                ENUM_TAKE_STOP_CALC_TYPE=self.take_stop_calc, 
                stop_loss=sl, 
                take_profit=tp, 
                INPUTS=AverageCrossLogic.INPUTS_AC_LOGIC(
                    fast_ma_inputs=MovingAverage.INPUTS_MA(fast_calc, fast_period),
                    slow_ma_inputs=MovingAverage.INPUTS_MA(slow_calc, slow_period),
                    trading_time=TimeToTrade(tm_op, tm_stp, tm_cls)
                )
            )
            for sl in stop_loss for tp in take_profit for slow_calc in slow_ma_calc_type for slow_period in slow_ma_period for fast_calc in fast_ma_calc_type for fast_period in fast_ma_period for tm_op in time_to_open_trades for tm_stp in time_to_stop_open for tm_cls in time_to_close_trades
        ]