import numpy as np
from numpy import *
import pandas as pd
import cufflinks as cf
cf.set_config_file(offline=True)

import warnings
warnings.filterwarnings('ignore')

class Prices():
    def __init__(self) -> None:
        pass

    def general_report(self, price_df) -> None:
        cf.iplot(self.candlesticks_plot(price_df))
        fig1=cf.subplots([
            self.normalized_plot(price_df),
            self.returns_plot(price_df)
        ], subplot_titles = [
            'Normalized plot',
            'Log Returns'
        ])
        cf.iplot(fig1)
        fig2=cf.subplots([
            self.histogram_plot(price_df),
            self.box_plot(price_df)
        ], subplot_titles = [
            'Histogram of Returns',
            'Boxplot of returns'
        ])
        cf.iplot(fig2)
        
    def candlesticks_plot(self,price_df):
        df_to_plot_candle = price_df.copy()
        df_to_plot_candle = df_to_plot_candle.set_index('time')
        return df_to_plot_candle.figure(kind='candle',title='Candlesticks',yTitle='Price', xTitle='Date')
    
    def normalized_plot(self,price_df):
        df_to_plot_normalized = price_df.copy()
        df_to_plot_normalized = df_to_plot_normalized.set_index('time')
        df_to_plot_normalized = df_to_plot_normalized['close']
        return df_to_plot_normalized.normalize().figure(title='Normalized plot',yTitle='Normalized result', xTitle='Date')
    
    def returns_plot(self,price_df):
        df_to_plot_returns = price_df.copy()
        df_to_plot_returns = df_to_plot_returns.set_index('time')
        df_to_plot_returns['returns'] = np.log(df_to_plot_returns['close']).diff()
        df_to_plot_returns.dropna()
        return df_to_plot_returns['returns'].figure(title='Log Returns', kind='bar',yTitle='Returns', xTitle='Date')
    
    def histogram_plot(self,price_df):
        df_to_plot_returns = price_df.copy()
        df_to_plot_returns['returns'] = np.log(df_to_plot_returns['close']).diff()
        return df_to_plot_returns['returns'].figure(kind='histogram', title = 'Histogram of Returns',yTitle='Count',xTitle='Returns')
    
    def box_plot(self,price_df):
        df_to_plot_returns = price_df.copy()
        df_to_plot_returns = df_to_plot_returns.set_index('time')
        df_to_plot_returns['returns'] = np.log(df_to_plot_returns['close']).diff()
        years = df_to_plot_returns.index.year.unique()
        newdf = pd.DataFrame()
        for year in years:
            newdf[year] = pd.Series(df_to_plot_returns[df_to_plot_returns.index.year==year]['returns']).reset_index(drop=True)
        newdf = newdf.ffill(axis=1)
        return newdf.figure(kind='box', 
            title='Boxplot of returns', 
            yTitle='Returns', 
            xTitle='Date',
            legend=False, boxpoints='outliers')
    
    def monte_carlo_simulation(self, data_df, horizon, timesteps, n_sims):
        s0 = data_df.iloc[-1]['close']
        data_df['returns'] = np.log(data_df['close']).diff()
        mu = data_df['returns'].mean()
        sigma = data_df['returns'].std()
        price_path = pd.DataFrame(self.__monte_carlo_paths(s0, mu, sigma, horizon, timesteps, n_sims))
        price_path.iloc[-1].iplot(kind='histogram', title= 'Simulated Geometric Brownian Motion at Maturity', bins=100)
        price_path.iloc[:,:min(100,len(price_path)-1)].iplot(title='Simulated Geometric Brownian Motion Paths (100 first simulations)', xTitle='Time Steps', yTitle='Index Levels')
        return price_path
    
    def __monte_carlo_paths(self, s0, mu, sigma, horizon, timesteps, n_sims):
        random.seed(10000) 
        S0 = s0         # initial spot level
        r = mu          # mu = rf in risk neutral framework 
        T = horizon     # time horizion
        t = timesteps   # number of time steps
        n = n_sims      # number of simulation
        dt = T/t
        S = zeros((t+1, n))
        S[0] = S0
        for i in range(1, t+1):
            z = random.standard_normal(n)
            S[i] = S[i-1] * exp((r - 0.5 * sigma ** 2) * dt + sigma * sqrt(dt) * z)
        return S