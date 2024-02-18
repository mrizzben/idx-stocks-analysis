import numpy as np
import pandas as pd

def log_rate(df):
    return np.log(df / df.shift(1)).dropna(how='all')

def daily_movt(open_price, close_price):
    return log_rate(close_price/open_price).fillna(0)

def risk_premium(stock_daily_return, daily_risk_free):
    stock_daily_return - daily_risk_free

def exp_weighted_corr(df, span=300):
    corr = df.ewm(span=span).corr()
    return corr.loc[corr.index.levels[0][-1]]

def exp_weighted_cov(df, span=300):
    cov = df.ewm(span=span).cov()
    return cov.loc[cov.index.levels[0][-1]]

def exp_weighted_std(df, span=300):
    std = df.ewm(span=span).std()
    return std.iloc[-1]

def label_point(x, y, val, ax):
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x'], point['y'], str(point['val']), fontweight='semibold', alpha=0.7)
