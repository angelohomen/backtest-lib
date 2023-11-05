from src.Backtest import Backtest
from src.utils.Log import Log
from datetime import datetime

class Optimizer():
    def __init__(
        self,
        symbol: str,
        ENUM_TIMEFRAME,
        trade_logic: list,
        limit_history: int
    ) -> None:
        Log.LogMsg(Log.ENUM_MSG_TYPE_INFO, f'Called Optimizer. Number of tests={(len(trade_logic)*len(ENUM_TIMEFRAME) if type(ENUM_TIMEFRAME)==list else len(trade_logic))}', time=datetime.now())
        self.__symbol=symbol
        self.__bt_list=[]
        self.__limit_history=limit_history
        counter=0
        for tl in trade_logic:
            if type(ENUM_TIMEFRAME)==list:
                self.ENUM_TIMEFRAME=ENUM_TIMEFRAME
                for _ in self.ENUM_TIMEFRAME:
                    self.__run_bt(tl, counter)
                    counter+=1
            else:
                self.ENUM_TIMEFRAME=ENUM_TIMEFRAME
                self.__run_bt(tl, counter)
            counter+=1

    def __run_bt(self, tl, counter):
        bt = Backtest(symbol=self.__symbol,ENUM_TIMEFRAME=self.ENUM_TIMEFRAME,trade_logic=tl,plot_report=False,backtest_name=f'opt/{counter}',limit_history=self.__limit_history)
        if bt: 
            Log.LogMsg(Log.ENUM_MSG_TYPE_INFO, 'Running backtest with inputs:', time=datetime.now())
            Log.LogMsg(Log.ENUM_MSG_TYPE_INFO, f'OPT {counter} | '+''.join([' | {0}={1} | '.format(k, v) for k,v in tl.get_current_inputs().items()]), time=datetime.now())
            bt.run()
        self.__bt_list.append({
                'inpts': tl.get_current_inputs(),
                'bt': bt
            })
    
    def get_max_result_bt(self):
        if len(self.__bt_list)==0:
            return None
        return max(self.__bt_list,key=lambda x: x['bt'].get_report_pointer().get_backtest_results()['returns'])
    
    def get_min_drawdown_bt(self):
        if len(self.__bt_list)==0:
            return None
        return min(self.__bt_list,key=lambda x: x['bt'].get_report_pointer().get_backtest_results()['max_drawdown'])
    
    def get_max_profit_factor_bt(self):
        if len(self.__bt_list)==0:
            return None
        return max(self.__bt_list,key=lambda x: x['bt'].get_report_pointer().get_backtest_results()['profit_factor'])