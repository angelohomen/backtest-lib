from datetime import datetime
import pandas as pd
from src.models.Trade import Trade
from src.models.Order import Order
from src.data_analysis.Report import Report
from src.TradeLogic import TradeLogic
from src.data_analysis.DataManipulation import DataManipulation
from src.data_analysis.Prices import Prices

class Backtest():

    def __init__(
            self,
            symbol: str,
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
                    mkt_data -> list:
                        Dataframe generated at src.data_analysis.DataManipulation with DataManipulation.PRICE_COLUMNS column order.
                    trade_logic -> TradeLogic:
                        Class that contains all logics from the trading strategy.
                    plot_report (optional) -> bool:
                        Insert True when needed to plot a backtest report.
                    backtest_name (optional) -> str:
                        When set, generates a csv with the backtest informations.
                    limit_history (optional) -> int:
                        Used to limit history informations to feed the trade logic, with minimum history, backtest will run faster. Do not set a maximum history with a value less than an indicators period.
        '''

        self.trades = []
        self.__symbol=symbol

        if not self.__initialize_mktdata():
            return print(f'[ERROR] Fail to download data from {self.__symbol}.')
        
        self.__trade_logic=trade_logic
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
        self.__df_ohlc = self.__dm.get_symbol_ohlc_df(self.__symbol,'TIMEFRAME_D1',1000000000000)
        self.__mkt_data=self.__df_ohlc.values
        return len(self.__mkt_data)>0

    def run(self):
        print('\r\nInitializing backtest\r\n')
        for i in range(len(self.__mkt_data)):
            if i == 0:
                continue
            last=True if i == len(self.__mkt_data)-1 else False
            to_pred=(self.__mkt_data[:i] if i<self.__limit_history else self.__mkt_data[(i-self.__limit_history):i]) if self.__limit_history else self.__mkt_data[:i]
            self.__trade_logic_predict(to_pred, i, last)
        print('\r\nFinish backtest\r\n')
        self.__report=Report(self.__name,self.__symbol,self.trades)
        if self.__plot_report:
            self.__report.plot_report()
        return self.trades

    def get_report_pointer(self):
        return self.__report

    def __trade_logic_predict(self, history, step, last=False):
        try:
            date = pd.to_datetime(history[-1][0])
            curr_close_price = history[-1][4]
        except:
            return print(f'Skipping {history[-1][0]} due to history lack of data.')

        self.__trade_logic.update(history,self.__curr_trade)

        signal=self.__trade_logic.trade_logic(step)

        if self.__curr_trade != None:
            self.__curr_trade.main(history[-1])
            if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_CLOSE:
                self.trades.append(self.__curr_trade)
                self.__curr_trade=None
                return
            if last or self.__trade_logic.close_trade_logic():
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    self.__curr_trade.close_trade(curr_close_price, date)
                    self.trades.append(self.__curr_trade)
                    self.__curr_trade=None
                    return
            if self.__trade_logic.modify_logic():
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    self.__curr_trade.modify_entry_stop_take(self.__trade_logic.new_sl,self.__trade_logic.new_tp)
                    return
        
        if signal == 1:
            if self.__curr_trade != None:
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if self.__curr_trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_SOLD:
                        self.__curr_trade.close_trade(curr_close_price, date)
                        self.trades.append(self.__curr_trade)
                        self.__curr_trade=None
            else:
                self.__curr_trade=self.__new_trade(Order.ENUM_ORDER_SIDE_BUY,self.__trade_logic.qty,curr_close_price,date,self.__trade_logic.stop_loss,self.__trade_logic.take_profit)
        if signal == -1:
            if self.__curr_trade != None:
                if self.__curr_trade.get_trade_info()['trade_state']==Trade.ENUM_TRADE_STATE_OPEN:
                    if self.__curr_trade.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT:
                        self.__curr_trade.close_trade(curr_close_price, date)
                        self.trades.append(self.__curr_trade)
                        self.__curr_trade=None
            else:
                self.__curr_trade=self.__new_trade(Order.ENUM_ORDER_SIDE_SELL,self.__trade_logic.qty,curr_close_price,date,self.__trade_logic.stop_loss,self.__trade_logic.take_profit)

    def __new_trade(
            self,
            ENUM_ORDER_SIDE,
            qty,
            price,
            time,
            stop_loss,
            take_profit
        ) -> Trade:
        return Trade(
                    Order(
                        self.__symbol,
                        ENUM_ORDER_SIDE,
                        qty,
                        price,
                        time
                    ),
                    self.__bot_id,
                    stop_loss,
                    take_profit
                )