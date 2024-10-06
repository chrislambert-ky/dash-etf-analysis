import dash
from dash import dcc, html, dash_table
from analysis import download_stock_data, find_buy_opportunities, calculate_growth, train_predictive_model, train_linear_model, create_stock_graph

# Download and process data for XLG
df = download_stock_data("XLG")
purchased = find_buy_opportunities(df, [0.99, 0.98, 0.97, 0.96, 0.95])
latest_price = df['Close'].iloc[-1]
purchased = calculate_growth(purchased, latest_price)
forecast = train_predictive_model(df)
linear_forecast = train_linear_model(df)

# Layout with graph and table for XLG
layout = html.Div([
    html.H1("XLG ETF Analysis"),

    # Graph for XLG with pattern-matching ID
    dcc.Graph(
        id={'type': 'stock-graph', 'index': 'xlg'},
        figure=create_stock_graph(df, purchased, forecast, linear_forecast)
    ),

    # Table for XLG purchases with pattern-matching ID
    dash_table.DataTable(
        id={'type': 'purchases-table', 'index': 'xlg'},
        columns=[
            {"name": "Date", "id": "Date"},
            {"name": "Symbol", "id": "Symbol"},
            {"name": "Buy Price", "id": "Buy_Price"},
            {"name": "Current Value", "id": "Current_Value"},
            {"name": "Growth", "id": "Growth"},
            {"name": "Growth Percentage", "id": "Growth_Percentage"}
        ],
        data=purchased.to_dict('records'),  # Initially, show all purchases
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_cell={'textAlign': 'center'},
    ),
])

# Expose the purchased DataFrame for use in app.py
purchased = purchased
