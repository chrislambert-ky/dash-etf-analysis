import dash
from dash import dcc, html

# Markdown content for the home page
markdown_text = """
# Welcome to the ETF Analysis Dashboard

_Disclaimer: The majority of this code was generated through various AI tools._

---

This dashboard provides detailed analysis and predictions for various Exchange-Traded Funds (ETFs). 
You can navigate through the different ETF pages using the sidebar.

### Features:
- **Historical stock data**
    - XLG - the largest 50 stocks in the S&P 500.
    - SPY - the S&P 500.
    - QQQ - the Nasdaq 100.
- **Buy-on-dip opportunities**
    - Based on my personal trading methodology of using conditional contingent orders to buy 1 share for every 1 percent drop in price.
- **Monitor long and short term trends** using:
    - **Linear Regression**
    - **Prophet Time Series Forecasting**

### How to Use the Dashboard:
1. Select an ETF from the sidebar to view detailed analysis.
2. Explore the graphs, tables, and predictions for each ETF.
3. Use the navigation to switch between different ETFs.

Visit the respective ETF pages for more information and analysis.
"""

# Layout of the home page with Markdown support
layout = html.Div([
    dcc.Markdown(markdown_text),  # Display the markdown content
])
