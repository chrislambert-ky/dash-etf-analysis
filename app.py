import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, MATCH
import dash_bootstrap_components as dbc
import pandas as pd
from pages import home, etf_xlg, etf_spy, etf_qqq
from analysis import find_buy_opportunities, calculate_growth

# Initialize the Dash app with suppress_callback_exceptions=True
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server  # Expose the Flask server for deployment

# Sidebar navigation
sidebar = html.Div(
    [
        html.H2("ETFs", className="display-4"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("XLG", href="/etf/xlg", active="exact"),
                dbc.NavLink("SPY", href="/etf/spy", active="exact"),
                dbc.NavLink("QQQ", href="/etf/qqq", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style={"position": "fixed", "top": 0, "left": 0, "bottom": 0, "width": "200px", "padding": "20px"},
)

# Content area for displaying the selected page
content = html.Div(id="page-content", style={"margin-left": "220px", "padding": "20px"})

# App layout
app.layout = html.Div([
    dcc.Location(id="url"),  # Tracks the current URL
    sidebar,
    content,
])

# Callback to update the page content dynamically
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/":
        return home.layout
    elif pathname == "/etf/xlg":
        return etf_xlg.layout
    elif pathname == "/etf/spy":
        return etf_spy.layout
    elif pathname == "/etf/qqq":
        return etf_qqq.layout
    else:
        return html.Div([
            html.H1("404: Page Not Found", className="text-danger"),
            html.P(f"The path '{pathname}' does not exist.")
        ])

# Callback for updating the table based on the zoomed-in area using Pattern-Matching IDs
@app.callback(
    Output({'type': 'purchases-table', 'index': MATCH}, 'data'),
    Input({'type': 'stock-graph', 'index': MATCH}, 'relayoutData'),
    State({'type': 'stock-graph', 'index': MATCH}, 'figure'),
    State('url', 'pathname')
)
def update_table_on_zoom(relayoutData, figure, pathname):
    # Determine which ETF page we're on based on the pathname
    if pathname == "/etf/xlg":
        purchased = etf_xlg.purchased
    elif pathname == "/etf/spy":
        purchased = etf_spy.purchased
    elif pathname == "/etf/qqq":
        purchased = etf_qqq.purchased
    else:
        return []  # Return empty data if not on a valid ETF page

    # Default to showing all purchases
    filtered_purchased = purchased

    # Check if the user has zoomed in
    if relayoutData and ('xaxis.range[0]' in relayoutData and 'xaxis.range[1]' in relayoutData):
        # Convert zoomed range to datetime
        start_date = pd.to_datetime(relayoutData['xaxis.range[0]'])
        end_date = pd.to_datetime(relayoutData['xaxis.range[1]'])

        # Filter the purchased DataFrame to only include rows within the zoomed range
        filtered_purchased = purchased[(purchased['Date'] >= start_date) & (purchased['Date'] <= end_date)]

    return filtered_purchased.to_dict('records')

if __name__ == "__main__":
    app.run_server(debug=True)
