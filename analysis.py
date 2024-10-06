import yfinance as yf
import pandas as pd
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go

# Download stock data from yfinance
def download_stock_data(ticker_symbol, period="10y", interval="1d"):
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(period=period, interval=interval)
    df = pd.DataFrame(data)
    df = df[['Open', 'High', 'Low', 'Close']]
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)  # Remove timezone information
    df['Symbol'] = ticker_symbol
    return df

# Identify buying opportunities based on price dips
def find_buy_opportunities(df, dip_levels):
    opportunities = []
    for _, row in df.iterrows():
        open_price = row['Open']
        low_price = row['Low']
        for level in dip_levels:
            target_price = open_price * level
            if low_price <= target_price:
                opportunities.append({
                    'Date': row['Date'],
                    'Symbol': row['Symbol'],
                    'Buy_Price': target_price,
                    'Buy_Level': f"{(1 - level) * 100:.1f}%"
                })
    return pd.DataFrame(opportunities)

# Calculate growth from purchase price to the latest price
def calculate_growth(purchased, latest_price):
    purchased['Current_Value'] = latest_price
    purchased['Growth'] = purchased['Current_Value'] - purchased['Buy_Price']
    purchased['Growth_Percentage'] = (purchased['Growth'] / purchased['Buy_Price']) * 100
    return purchased

# Prophet model for stock price prediction
def train_predictive_model(df):
    model_df = df[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})
    model = Prophet()
    model.fit(model_df)
    future = model.make_future_dataframe(periods=365)
    forecast = model.predict(future)
    return forecast

# Linear regression model for stock price prediction
def train_linear_model(df):
    # Convert the date to ordinal numbers for regression
    df['Date_ordinal'] = pd.to_datetime(df['Date']).map(pd.Timestamp.toordinal)
    X = df[['Date_ordinal']]  # Use DataFrame with the column name 'Date_ordinal'
    y = df['Close']
    
    # Scale the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train the Linear Regression model
    model = LinearRegression()
    model.fit(X_scaled, y)
    
    # Create a continuous date range from the start of the dataset to 12 months into the future
    full_date_range = pd.date_range(start=df['Date'].min(), end=df['Date'].max() + pd.DateOffset(days=365), freq='D')
    
    # Convert the full date range to ordinal values
    full_date_range_ordinal = full_date_range.map(pd.Timestamp.toordinal).values.reshape(-1, 1)
    
    # Convert the full date range to DataFrame with the same column name 'Date_ordinal'
    full_date_range_ordinal_df = pd.DataFrame(full_date_range_ordinal, columns=['Date_ordinal'])
    
    # Scale the full date range using the same scaler
    full_date_range_scaled = scaler.transform(full_date_range_ordinal_df)
    
    # Predict for both historical and future dates
    full_predictions = model.predict(full_date_range_scaled)
    
    # Create a DataFrame for the full predictions (historical + future)
    linear_forecast = pd.DataFrame({
        'Date': full_date_range,
        'Predicted_Close': full_predictions
    })
    
    return linear_forecast



# Create the stock graph visualization
def create_stock_graph(df, purchased, forecast, linear_forecast):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['High'],
        mode='lines',
        name='High Price',
        line=dict(color='rgba(0, 100, 80, 0.5)')
    ))
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Low'],
        mode='lines',
        name='Low Price',
        fill='tonexty',
        line=dict(color='rgba(0, 100, 80, 0.5)')
    ))

    fig.add_trace(go.Scatter(
        x=purchased['Date'],
        y=purchased['Buy_Price'],
        mode='markers',
        name='Buy-on-Dip Opportunities',
        marker=dict(color='red', size=5)
    ))

    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        mode='lines',
        name='Prophet Predicted Close Price',
        line=dict(color='blue', dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=linear_forecast['Date'],
        y=linear_forecast['Predicted_Close'],
        mode='lines',
        name='Linear Regression Predicted Close Price',
        line=dict(color='orange', dash='dot')
    ))

    fig.update_layout(
        title='Stock Prices and Buy-on-Dip Opportunities',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        height=600
    )
    return fig
