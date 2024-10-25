
 
import eikon as ek
import pandas as pd
import statsmodels.api as sm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
 

API_KEY = ''
ek.set_app_key(API_KEY)
 
# Define the date range and RIC codes
start_date = '2019-01-01'
end_date = '2024-07-30'
spot_ric = 'CHF='
forward_ric = 'CHF1M='  # Correct RIC for 1-month forward rate
 
# Fetch daily spot rates for USD/JPY
try:
    spot_data = ek.get_timeseries(spot_ric,
                                  fields='CLOSE',
                                  start_date=start_date,
                                  end_date=end_date,
                                  interval='daily')
except Exception as e:
    print(f"Error fetching spot rates: {e}")
    spot_data = pd.DataFrame()
 
# Fetch daily forward rates for USD/JPY (30 days forward)
try:
    forward_data = ek.get_timeseries(forward_ric,
                                     fields='CLOSE',
                                     start_date=start_date,
                                     end_date=end_date,
                                     interval='daily')
except Exception as e:
    print(f"Error fetching forward rates: {e}")
    forward_data = pd.DataFrame()
 
if not spot_data.empty and not forward_data.empty:
    # Data Preparation
    spot_data = spot_data.reset_index()
    spot_data.columns = ['Date', 'Spot Rate']
 
    forward_data = forward_data.reset_index()
    forward_data.columns = ['Date', 'Forward Rate (30 Days)']
 
 
    data = pd.merge(spot_data, forward_data, on='Date')
 
    # Construct Variables for 30-day forecast
    data['X'] = data['Forward Rate (30 Days)'] - data['Spot Rate']
    data['Y'] = data['Spot Rate'].shift(-30) - data['Spot Rate']
 
  
    data.dropna(inplace=True)
 
   
    data['X'] = data['X'].astype(float)
    data['Y'] = data['Y'].astype(float)
 
    # Regression Analysis
    X = data['X']
    Y = data['Y']
    X = sm.add_constant(X) 
 
    model = sm.OLS(Y, X).fit()
 

    print("Regression Analysis Results:")
    print(model.summary())
 
    # Trading Strategy Simulation
    data['Position'] = data.apply(lambda row: 'buy' if row['X'] > row['Y'] else 'sell', axis=1)
    data['Return'] = 0.0
 
    for i in range(len(data) - 30):
        if data.iloc[i]['Position'] == 'buy':
            data.at[i, 'Return'] = data.iloc[i + 30]['Spot Rate'] - data.iloc[i]['Spot Rate']
        else:
            data.at[i, 'Return'] = data.iloc[i]['Spot Rate'] - data.iloc[i + 30]['Spot Rate']
 
    avg_return = data['Return'].mean()
    std_return = data['Return'].std()
    total_return = data['Return'].sum()
 
    print("\nTrading Strategy Performance Metrics:")
    print(f'Average Return: {avg_return}')
    print(f'Standard Deviation of Returns: {std_return}')
    print(f'Total Return: {total_return}')
 
    #  profit or loss
    data['Profit/Loss'] = data['Return'].apply(lambda x: 'Profit' if x > 0 else 'Loss')
    profit_loss_counts = data['Profit/Loss'].value_counts()
 
    print("\nProfit/Loss Analysis:")
    print(profit_loss_counts)
 
    # Backtesting: Calculate Cumulative Returns
    data['Cumulative Return'] = data['Return'].cumsum()
 
    # Plotting using Plotly
    fig = make_subplots(rows=4, cols=1, subplot_titles=('Regression Analysis', 'Trading Strategy Returns', 'Profit/Loss from Trading Strategy', 'Cumulative Returns'))
 
    # Regression Analysis Plot
    fig.add_trace(go.Scatter(x=data['X'], y=data['Y'], mode='markers', name='Data Points'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['X'], y=model.fittedvalues, mode='lines', name='Fitted Line', line=dict(color='red')), row=1, col=1)
 
    # Trading Strategy Returns Plot
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Return'], mode='lines', name='Returns'), row=2, col=1)
 
    # Profit/Loss Bar Chart
    colors = ['rgba(0, 255, 0, 0.5)' if val == 'Profit' else 'rgba(255, 0, 0, 0.5)' for val in data['Profit/Loss']]
    fig.add_trace(go.Bar(x=data['Date'], y=data['Return'], marker_color=colors, name='PnL', width=86400000 * 20), row=3, col=1)
 
    # Cumulative Returns Plot
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Cumulative Return'], mode='lines', name='Cumulative Returns'), row=4, col=1)
 
    # Update layout
    fig.update_layout(height=1200, width=1200, title_text='Daily Exchange Rate Analysis and Trading Strategy with Backtesting', showlegend=False)
    fig.update_xaxes(title_text='X (Forward Rate - Spot Rate)', row=1, col=1)
    fig.update_xaxes(title_text='Date', row=2, col=1)
    fig.update_xaxes(title_text='Date', row=3, col=1)
    fig.update_xaxes(title_text='Date', row=4, col=1)
    fig.update_yaxes(title_text='Y (Future Spot Rate - Spot Rate)', row=1, col=1)
    fig.update_yaxes(title_text='Return', row=2, col=1)
    fig.update_yaxes(title_text='PnL', row=3, col=1)
    fig.update_yaxes(title_text='Cumulative Return', row=4, col=1)
 
    fig.show()
 
else:
    print("Failed to fetch necessary data.")



 