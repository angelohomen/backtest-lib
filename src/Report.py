import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline
import seaborn as sns
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')
from src.Trade import Trade

class Report():
    def __init__(self, name, symbol, trades):
        self.__can_generate_report = len(trades)>0
        if not self.__can_generate_report:
            return print('No trades')

        self.__report_data=pd.DataFrame(list(map(lambda x: {
            'EntryTime': x.get_trade_info()['trade_creation_time'],
            'ExitTime': x.get_trade_info()['trade_out_time'],
            'TradeSide': x.get_trade_info()['trade_side'],
            'TradeResult': 
                x.get_trade_info()['entry_order']['avg_fill_price']*x.get_trade_info()['entry_order']['filled_volume']-x.get_trade_info()['out_order']['avg_fill_price']*x.get_trade_info()['out_order']['filled_volume']
                if x.get_trade_info()['trade_side']==Trade.ENUM_TRADE_SIDE_BOUGHT else
                -x.get_trade_info()['entry_order']['avg_fill_price']*x.get_trade_info()['entry_order']['filled_volume']+x.get_trade_info()['out_order']['avg_fill_price']*x.get_trade_info()['out_order']['filled_volume']
        },trades)))
        self.__result_df=pd.DataFrame()
        self.__backtest_results:dict={}
        self.__calculate_parameters()
        self.__symbol=symbol
        self.__name=name

    def __calculate_parameters(self):
        if not self.__can_generate_report:
            return print('No trades')

        self.__result_df=self.__report_data.copy()
        self.__result_df['EntryTime'] = pd.to_datetime(self.__result_df['EntryTime'])
        self.__result_df.loc[self.__result_df['TradeResult']>0,'TradeType'] = 'Profit'
        self.__result_df.loc[self.__result_df['TradeResult']<0,'TradeType'] = 'Loss'
        self.__result_df.loc[self.__result_df['TradeResult']==0,'TradeType'] = 'None'
        total = self.__result_df.groupby('TradeType')['TradeResult'].sum()
        totalProfit = total['Profit']
        totalLoss = total['Loss']
        qty = self.__result_df.groupby('TradeType').size()
        qtyNone = qty['None'] if 'None' in qty.index else 0

        # Report parameters result
        # Number of operations
        totalOp = len(self.__result_df.index)

        # Gross Profit and winner trades
        grossProfit=totalProfit
        qtyProfit = qty['Profit'] if 'Profit' in qty.index else 0

        # Gross Loss and losing trades
        grossLoss=round(totalLoss,2)
        qtyLoss = qty['Loss'] if 'Loss' in qty.index else 0

        # Profit Trades (% of total)
        profitTradesPerc = 100*qtyProfit/totalOp

        # Profit factor
        profitFactor = abs(totalProfit/totalLoss)

        # Max 
        largestProfitTrade = self.__result_df['TradeResult'].max()
        largestLossTrade = self.__result_df['TradeResult'].min()

        # Average result for each trade type
        med = self.__result_df.groupby('TradeType')['TradeResult'].mean()
        medProfit = med['Profit'] if 'Profit' in med.index else 0
        medLoss = med['Loss'] if 'Loss' in med.index else 0
        medNone = med['None'] if 'None' in med.index else 0      

        returns = (qtyProfit*medProfit) + (qtyLoss*medLoss)
        self.__result_df['Balance'] = self.__result_df['TradeResult'].cumsum()
        self.__result_df['BalanceMaxAc'] = self.__result_df['Balance'].cummax()
        self.__result_df['Drawdowns'] = self.__result_df['BalanceMaxAc'] - self.__result_df['Balance']
        self.__endDD = self.__result_df['Drawdowns'].idxmax()
        self.__initDD = self.__result_df['BalanceMaxAc'].iloc[:self.__endDD].idxmax()
        self.__dateInitDD = self.__result_df['EntryTime'].iloc[self.__initDD]
        self.__dateEndDD = self.__result_df['EntryTime'].iloc[self.__endDD]
        self.__initBalance = self.__result_df['Balance'].iloc[self.__initDD]
        self.__endBalance = self.__result_df['Balance'].iloc[self.__endDD]
        MDD = self.__result_df['Drawdowns'].max()
        retornoPerc = 100*returns/MDD

        self.__backtest_results={
            'total_trades': totalOp,
            'gross_profit': totalProfit,
            'gross_loss': totalLoss,
            'qty_profit': qtyProfit,
            'qty_loss': qtyLoss,
            'qty_none': qtyNone,
            'profit_trades_perc': profitTradesPerc,
            'profit_factor': profitFactor,
            'max_winner_result': largestProfitTrade,
            'max_loss_result': largestLossTrade,
            'average_profit': medProfit,
            'average_loss': medLoss,
            'max_drawdown': MDD,
            'returns': returns,
            'perc_returns': retornoPerc
        }
    
    def get_backtest_results(self):
        return self.__backtest_results

    def plot_report(self):
        if not self.__can_generate_report:
            return print('No trades')

        if self.__name:
            print(f'\r\n\t\t\t\t\tTrading {self.__name} ({self.__symbol}) backtest:\r\n')
        else:
            print(f'\r\n\t\t\t\t\tTrading {self.__symbol} backtest:\r\n')

        # Write
        print('Gross Profit: \t\t\t', round(self.__backtest_results['gross_profit'],2), end='\t\t\t')
        print('Winner trades: ', self.__backtest_results['qty_profit'])
        print('Gross Loss: \t\t\t', round(self.__backtest_results['gross_loss'],0), end='\t\t\t')
        print('Losing trades: ', self.__backtest_results['qty_loss'])
        print('Profit Trades (% of total): \t', round(self.__backtest_results['profit_trades_perc'],2),'%')
        print('Profit factor: \t\t\t', round(self.__backtest_results['profit_factor'],2))
        print('Largest profit trade: \t\t', round(self.__backtest_results['max_winner_result'],2), end='\t\t\t\t')
        print('Largest loss trade: ', round(self.__backtest_results['max_loss_result'],2))
        print('Average profit trade: \t\t', round(self.__backtest_results['average_profit'],2), end='\t\t\t\t')
        print('Average loss trade: ', round(self.__backtest_results['average_loss'],2), '\n')
        print('Profit/Loss: \t\t\t', abs(round(self.__backtest_results['average_profit']/self.__backtest_results['average_loss'],2)))
        print('Total Net profit: \t\t', round(self.__backtest_results['returns'], 2))
        print('Percentual return: \t\t', round(self.__backtest_results['perc_returns'],2), '%\n')
        print('Balance Drawdown Maximal: \t', round(self.__backtest_results['max_drawdown'],2))
        print('Balance Drawdown Maximal Time Range:', self.__dateInitDD, ' until ', self.__dateEndDD)
        
        fig = plt.figure(figsize=(15, 25))
        axPizza = fig.add_subplot(5, 2, 1)
        axBar = fig.add_subplot(5, 2, 2)
        axHist = fig.add_subplot(5, 2, 3)
        axScatter = fig.add_subplot(5, 2, 4) 
        axLine = fig.add_subplot(5, 2, (5,6)) 
        axHour = fig.add_subplot(5, 2, 7)
        axWeek = fig.add_subplot(5, 2, 8)
        axMonth = fig.add_subplot(5, 2, (9,10))

        # PLOT
        # Pizza
        axPizza.set_title('Profit, Loss, and Neutral Positions (%)')
        sizes = [self.__backtest_results['qty_profit'], self.__backtest_results['qty_loss'], self.__backtest_results['qty_none']]
        labels = 'Profit', 'Loss', 'Equilibrium' 
        axPizza.pie(sizes, labels=labels, autopct='%1.2f%%',
                    colors=['#6DC75E','#D6675A','#5CA8DA'],
                    textprops={'fontsize': 14})

        # Bar
        axBar.set_title('Average for Positive and Negative Balance ')
        sns.barplot(data=self.__result_df, x='TradeType', y='TradeResult',
                    order=['Profit', 'Loss', 'None'],
                    palette=['#6DC75E','#D6675A','#5CA8DA'],
                    ax=axBar)

        # Hist
        axHist.set_title('Balance Distribution ')
        sns.distplot(self.__result_df['TradeResult'], ax=axHist)

        # Scatter
        axScatter.set_title('Balance Scatter ')
        self.__result_df.plot(x='EntryTime', y='TradeResult',kind='scatter',
                    ax=axScatter, alpha=.7, s=10)
            
        # Balance and Drawdown lines
        axLine.set_title('Balance and Maximum Drawdown')
        self.__result_df.plot(x='EntryTime', y='BalanceMaxAc',
                    label='MaxCum', ax=axLine)

        self.__result_df.plot(x='EntryTime', y='Balance', 
                    label='Balance', ax=axLine)

        self.__result_df.plot(x='EntryTime', y='Drawdowns',
                    label='Drawdowns', ax=axLine, linewidth=.8)
        
        # Drawdown range
        axLine.plot([self.__dateInitDD, self.__dateEndDD], [self.__initBalance, self.__endBalance],
                    marker='o', linestyle='--',
                    color='purple', label='MDD')
                
        # HOUR
        auxHour = self.__result_df.drop(['TradeType','TradeSide'],axis=1).groupby(by=self.__result_df['EntryTime'].dt.hour).mean()

        if len(auxHour.index) > 1: 
            cond = [(auxHour['TradeResult']>=0.0), (auxHour['TradeResult']<0.0)]
            esc = ['High', 'Low']
            auxHour['Color'] = np.select(cond, esc, default=None)
            order = auxHour.index.sort_values().unique().values
            axHour.set_title('Net Balance per hour ')
            if len(auxHour[auxHour['TradeResult']>0])>0:
                sns.barplot(x=auxHour[auxHour['TradeResult']>0].index, y='TradeResult',data=auxHour[auxHour['TradeResult']>0], order=order,            
                        color='#6DC75E', ax=axHour)
            if len(auxHour[auxHour['TradeResult']<0])>0:
                sns.barplot(x=auxHour[auxHour['TradeResult']<0].index, y='TradeResult',data=auxHour[auxHour['TradeResult']<0], order=order,            
                        color='#D6675A', ax=axHour)

        # WEEK DAYS
        auxWeek = self.__result_df.drop(['TradeType','TradeSide'],axis=1).groupby(by=self.__result_df['EntryTime'].dt.day_name()).mean()

        if len(auxWeek.index) > 1: 
            cond = [(auxWeek['TradeResult']>=0.0), (auxWeek['TradeResult']<0.0)]
            esc = ['High', 'Low']
            auxWeek['Color'] = np.select(cond, esc, default=None)
            order = ['Monday', 'Tuesday','Wednesday', 'Thursday','Friday']
            axWeek.set_title('Net Balance per day ')
            if len(auxWeek[auxWeek['TradeResult']>0])>0:
                sns.barplot(x=auxWeek[auxWeek['TradeResult']>0].index, y='TradeResult',data=auxWeek[auxWeek['TradeResult']>0], order=order,            
                        color='#6DC75E', ax=axWeek)
            if len(auxWeek[auxWeek['TradeResult']<0])>0:
                sns.barplot(x=auxWeek[auxWeek['TradeResult']<0].index, y='TradeResult',data=auxWeek[auxWeek['TradeResult']<0], order=order,            
                        color='#D6675A', ax=axWeek)

        #MONTH
        auxMonth = self.__result_df.drop(['TradeType','TradeSide'],axis=1).groupby(by=self.__result_df['EntryTime'].dt.month_name()).mean()

        if len(auxMonth.index) > 1: 
            # Cria condição para a escolha da Color
            cond = [(auxMonth['TradeResult']>=0.0), (auxMonth['TradeResult']<0.0)]
            esc = ['High', 'Low']
            auxMonth['Color'] = np.select(cond, esc, default=None)
            order = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                    'August', 'September', 'October', 'November', 'December']
            axMonth.set_title('Net Balance per month ')
            if len(auxMonth[auxMonth['TradeResult']>0])>0:
                sns.barplot(x=auxMonth[auxMonth['TradeResult']>0].index, y='TradeResult',data=auxMonth[auxMonth['TradeResult']>0], order=order,            
                        color='#6DC75E', ax=axMonth)
            if len(auxMonth[auxMonth['TradeResult']<0])>0:
                sns.barplot(x=auxMonth[auxMonth['TradeResult']<0].index, y='TradeResult',data=auxMonth[auxMonth['TradeResult']<0], order=order,            
                        color='#D6675A', ax=axMonth)
        plt.tight_layout()