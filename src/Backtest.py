from datetime import datetime
import pandas as pd
from src.utils.Log import Log
from src.models.Trade import Trade
from src.models.Order import Order
from src.TradeLogic import TradeLogic
from src.data_analysis.Report import Report
from src.data_analysis.Prices import Prices
from src.data_analysis.DataManipulation import DataManipulation

class Backtest():

        # Backtest possible timeframes
    ENUM_TIMEFRAME_M1='TIMEFRAME_M1'
    ENUM_TIMEFRAME_M2='TIMEFRAME_M2'
    ENUM_TIMEFRAME_M3='TIMEFRAME_M3'
    ENUM_TIMEFRAME_M4='TIMEFRAME_M4'
    ENUM_TIMEFRAME_M5='TIMEFRAME_M5'
    ENUM_TIMEFRAME_M6='TIMEFRAME_M6'
    ENUM_TIMEFRAME_M10='TIMEFRAME_M10'
    ENUM_TIMEFRAME_M12='TIMEFRAME_M12'
    ENUM_TIMEFRAME_M15='TIMEFRAME_M15'
    ENUM_TIMEFRAME_M20='TIMEFRAME_M20'
    ENUM_TIMEFRAME_M30='TIMEFRAME_M30'
    ENUM_TIMEFRAME_H1='TIMEFRAME_H1'
    ENUM_TIMEFRAME_H2='TIMEFRAME_H2'
    ENUM_TIMEFRAME_H3='TIMEFRAME_H3'
    ENUM_TIMEFRAME_H4='TIMEFRAME_H4'
    ENUM_TIMEFRAME_H6='TIMEFRAME_H6'
    ENUM_TIMEFRAME_H8='TIMEFRAME_H8'
    ENUM_TIMEFRAME_H12='TIMEFRAME_H12'
    ENUM_TIMEFRAME_D1='TIMEFRAME_D1'
    ENUM_TIMEFRAME_W1='TIMEFRAME_W1'
    ENUM_TIMEFRAME_MN1='TIMEFRAME_MN1'
    ENUM_TIMEFRAME_MN3='TIMEFRAME_MN3'
    ENUM_TIMEFRAME_Y1='TIMEFRAME_Y1'
    ENUM_TIMEFRAME_Y2='TIMEFRAME_Y2'
    ENUM_TIMEFRAME_Y5='TIMEFRAME_Y5'
    ENUM_TIMEFRAME_Y10='TIMEFRAME_Y10'

    def __init__(
            self,
            symbol: str,
            ENUM_TIMEFRAME: str,
            trade_logic: TradeLogic,
            plot_report: bool=False,
            backtest_name: str=None,
            limit_history: int=None,
            bot_id: int=-1
        ):
        '''
            "Backtest()" is a class to test a trading algorithm.
            --------------------------------------------------------------------------
                Parameters
                    symbol -> str:
                        Symbol to backtest.
                    ENUM_TIMEFRAME -> str:
                        Timeframe of data to backtest.
                    trade_logic -> TradeLogic:
                        Class that contains all logics from the trading strategy.
                    plot_report (optional) -> bool:
                        Insert True when needed to plot a backtest report.
                    backtest_name (optional) -> str:
                        When set, generates a csv with the backtest informations.
                    limit_history (optional) -> int:
                        Used to limit history informations to feed the trade logic, with minimum history, backtest will run faster. Do not set a maximum history with a value less than an indicators period.
                    bot_id -> int (optional):
                        Bot ID to manage more than one, if needed.
                    log -> bool (optional):
                        Set True if want to retrieve bot logs.
        '''

        self.trades = []
        self.__symbol=symbol
        self.__ENUM_TIMEFRAME=ENUM_TIMEFRAME
        self.__trade_logic=trade_logic
        self.__log=self.__trade_logic.log

        if not self.__initialize_mktdata():
            if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_ERROR,msg=f'Fail to download data from {self.__symbol}.',time=datetime.now())
            return
        
        self.__curr_trade:Trade=None
        self.__report=None
        self.__plot_report=plot_report
        self.__name=backtest_name
        self.__limit_history=limit_history
        self.__trade_logic.set_full_history(self.__mkt_data)
        self.__bot_id=bot_id

        if self.__plot_report:
            self.__px.general_report(self.__df_ohlc)
            self.__px.monte_carlo_simulation(self.__df_ohlc, 1, 252, 100000)

    def __initialize_mktdata(self):
        self.__dm = DataManipulation()
        self.__px = Prices()
        if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Retrieving {self.__symbol} data.',time=datetime.now())
        self.__df_ohlc = self.__dm.get_symbol_ohlc_df(self.__symbol,self.__ENUM_TIMEFRAME,1000000000000)
        self.__mkt_data=self.__df_ohlc.values
        if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Finish downloading data from {self.__symbol}, length={len(self.__mkt_data)}.',time=datetime.now())
        return len(self.__mkt_data)>0

    def run(self):
        if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg='Initializing backtest.',time=datetime.now())
        for i in range(len(self.__mkt_data)):
            if i == 0:
                continue
            last=True if i == len(self.__mkt_data)-1 else False
            to_pred=(self.__mkt_data[:i] if i<self.__limit_history else self.__mkt_data[(i-self.__limit_history):i]) if self.__limit_history else self.__mkt_data[:i]
            self.__trade_logic_predict(to_pred, i, last)
        if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg='Finish backtest.',time=datetime.now())
        self.__report=Report(self.__name,self.__symbol,self.trades)
        if self.__plot_report:
            self.__report.plot_report()
        Log.LogClose()
        return self.trades

    def get_report_pointer(self):
        return self.__report

    def __trade_logic_predict(self, history, step, last=False):
        try:
            date = pd.to_datetime(history[-1][self.__dm.get_data_idx('time')])
            curr_close_price = history[-1][self.__dm.get_data_idx('close')]
        except:
            if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg='Skipping {date} due to history lack of data.',time=datetime.now())
            return

        self.__trade_logic.update(history,self.__curr_trade)

        signal=self.__trade_logic.trade_logic(step)

        if self.__curr_trade != None:
            self.__curr_trade.main(history[-1])
            if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_CLOSE:
                self.__trade_finish(date)
                return
            if last or self.__trade_logic.close_trade_logic():
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Closing trade ({self.__curr_trade.get_trade_info()["trade_id"]}) due to {("last mkt data" if last else "close logic")}.',time=date)
                    self.__curr_trade.close_trade(curr_close_price)
                    self.__trade_finish(date)
                    return
            if self.__trade_logic.modify_logic():
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    self.__curr_trade.modify_entry_stop_take(self.__trade_logic.new_sl,self.__trade_logic.new_tp)
                    return
        
        if self.__curr_trade == None:
            if signal == 1:
                self.__curr_trade=self.__new_trade(Order.ENUM_ORDER_SIDE_BUY,self.__trade_logic.qty,0,date,self.__trade_logic.stop_loss,self.__trade_logic.take_profit,self.__trade_logic.take_stop_calc)
            if signal == -1:
                self.__curr_trade=self.__new_trade(Order.ENUM_ORDER_SIDE_SELL,self.__trade_logic.qty,0,date,self.__trade_logic.stop_loss,self.__trade_logic.take_profit,self.__trade_logic.take_stop_calc)

    def __trade_finish(self,time):
        if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'Append trade ({self.__curr_trade.get_trade_info()["trade_id"]}) to list of done trades.',time=time)
        self.trades.append(self.__curr_trade)
        self.__curr_trade=None

    def __new_trade(
            self,
            ENUM_ORDER_SIDE,
            qty,
            price,
            time,
            stop_loss,
            take_profit,
            calc_type
        ) -> Trade:
        new_trade=Trade(
                    Order(
                        self.__symbol,
                        ENUM_ORDER_SIDE,
                        qty,
                        price,
                        time,
                        log=self.__log
                    ),
                    self.__bot_id,
                    stop_loss,
                    take_profit,
                    calc_type,
                    self.__log
                )
        if self.__log: Log.LogMsg(ENUM_MSG_TYPE=Log.ENUM_MSG_TYPE_INFO,msg=f'New trade ({new_trade.get_trade_info()["trade_id"]}).',time=time)
        return new_trade