import yfinance as yf
import pandas as pd

def get_stock_data(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")
    return {
        "current_price": hist['Close'][-1],
        "atr": hist['High'].sub(hist['Low']).rolling(14).mean().iloc[-1],
        "beta": stock.info.get('beta')
    }

print(get_stock_data("RELIANCE.NS"))
