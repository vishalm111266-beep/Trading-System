
import yfinance as yf
import pandas as pd
import sys

def get_fundamental_analysis(ticker):
    stock = yf.Ticker(ticker)

    # Get stock info
    info = stock.info

    # Company Overview
    sector = info.get('sector', 'N/A')
    market_cap = info.get('marketCap', 'N/A')
    long_business_summary = info.get('longBusinessSummary', 'N/A')

    # Financial Health
    financials = stock.financials
    balance_sheet = stock.balance_sheet
    cashflow = stock.cashflow

    revenue_growth = (financials.loc['Total Revenue'].pct_change().iloc[-1] * 100) if not financials.loc['Total Revenue'].empty else 'N/A'
    net_income = financials.loc['Net Income'] if 'Net Income' in financials.index else 'N/A'
    total_revenue = financials.loc['Total Revenue'] if 'Total Revenue' in financials.index else 'N/A'
    net_profit_margin = (net_income.iloc[-1] / total_revenue.iloc[-1]) * 100 if isinstance(net_income, pd.Series) and isinstance(total_revenue, pd.Series) and not total_revenue.empty and total_revenue.iloc[-1] != 0 else 'N/A'

    roe = info.get('returnOnEquity', 'N/A')
    debt_to_equity = info.get('debtToEquity', 'N/A')

    # Valuation
    pe_ratio = info.get('trailingPE', 'N/A')
    industry_pe = info.get('industryPE', 'N/A')
    peg_ratio = info.get('pegRatio', 'N/A')
    ev_to_ebitda = info.get('enterpriseToEbitda', 'N/A')

    # Competitive Position
    market_share = 'N/A' # This data is not available from yfinance

    # --- Output ---
    print(f"STOCK: {ticker}")
    print(f"MARKET: INDIAN")
    print("\nCOMPANY OVERVIEW:")
    print(f"- Sector: {sector}")
    print(f"- Market Cap: {market_cap}")
    print(f"- Business Description: {long_business_summary[:200]}...") # Truncate for brevity

    print("\nFINANCIAL HEALTH: [MODERATE]") # Placeholder, needs logic
    print(f"- Revenue Growth: {revenue_growth:.2f}%")
    print(f"- Profit Margin: {net_profit_margin:.2f}%")
    print(f"- ROE: {roe * 100:.2f}%" if isinstance(roe, float) else roe)
    print(f"- Debt/Equity: {debt_to_equity}")

    print("\nVALUATION: [FAIR]") # Placeholder, needs logic
    print(f"- P/E: {pe_ratio:.2f}" if isinstance(pe_ratio, float) else pe_ratio)
    print(f"- PEG: {peg_ratio}")
    print(f"- EV/EBITDA: {ev_to_ebitda}")

    print("\nCOMPETITIVE POSITION: [STRONG]") # Placeholder, needs logic
    print(f"- Moat: WIDE") # Placeholder
    print(f"- Market Share: {market_share}")

    print("\nINVESTMENT THESIS:")
    print("[Bull and bear case arguments here]")

    print("\nRECOMMENDATION: [HOLD]")
    print("TARGET PRICE: [LEVEL]")
    print("TIME HORIZON: [1Y]")
    print("\nRISK DISCLAIMER: This is fundamental analysis, not financial advice.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
        get_fundamental_analysis(ticker)
    else:
        print("Please provide a stock ticker.")

