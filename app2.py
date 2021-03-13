import streamlit as st
import pandas as pd
from PIL import Image
import pandas_datareader as web
import requests
import numpy as np
import base64
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

st.title('Stock Market Web Application')

st.markdown("""
**Visually** show data on a stock!
 """)

image = Image.open("image2.png")
st.image(image,use_column_width=True)


st.header("""User Guide """)
st.write("1.Filter your interested sectors of companies")
st.write("2.Enter a Ticker")
st.write("3.Enter a Start Date and End Date ")
st.write("4.Choose Indicator")
st.write("5.Check the boxes if you want to know more about the Stock")
st.write("6.Follow the instruction of the indicators to Interpret the Indicators")
#create a sidebar header
st.sidebar.header('User Input Parameter')


@st.cache
def load_data():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')

# Sidebar - Sector selection
sorted_sector_unique = sorted( df['GICS Sector'].unique() )
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Filtering data
df_selected_sector = df[ (df['GICS Sector'].isin(selected_sector)) ]

st.header('Companies in Selected Sector')
st.write('Data Dimension: ' + str(df_selected_sector.shape[0]) + ' rows and ' + str(df_selected_sector.shape[1]) + ' columns.')
st.dataframe(df_selected_sector)

# Download S&P500 data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_sector), unsafe_allow_html=True)

df2 = pd.read_csv('Forex.csv')
st.header('Forex Symbol')
st.write(df2)

df3 = pd.read_csv('commodities.csv')
st.header('Commodities Symbol')
st.write(df3)


today = datetime.date.today()
def user_input_features():
    ticker = st.sidebar.text_input("Ticker","^HSI")
    start_date = st.sidebar.date_input('start date', datetime.date(2018,1,1))
    end_date = st.sidebar.date_input("End Date", today)
    #information = st.sidebar.selectbox('Information',('Close','Volume','Canlestick'))
    options = ['Select Indicator','Bollinger Bands with RSI','MACD', 'OBV']
    indicator_selection1 = st.sidebar.selectbox(
        label='Indicator 1',
        options=options)

    indicator_selection2 = st.sidebar.selectbox(
         label = 'Indicator 2',
         options = options)

    indicator_selection3 = st.sidebar.selectbox(
         label = 'Indicator 3',
         options = options)

    return ticker, start_date, end_date,indicator_selection1,indicator_selection2,indicator_selection3

symbol, start, end , indicator_selection1,indicator_selection2,indicator_selection3 = user_input_features()

def get_symbol(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
    result = requests.get(url).json()
    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']
company_name = get_symbol(symbol.upper())

start = pd.to_datetime(start)
end = pd.to_datetime(end)

# Read data
data = web.DataReader(symbol,'yahoo', start, end)
data.to_csv('histdata.csv')
data = pd.read_csv('histdata.csv')
data = data.set_index(pd.DatetimeIndex(data['Date'].values))
#visualising
if st.checkbox('Show Daily Candlestick Chart'):
    fig = go.Figure()
    fig.add_trace(
            go.Candlestick(x=data["Date"], open=data["Open"],
                   high=data["High"], low=data["Low"], close=data["Close"]))
    fig.update_layout(
        autosize=False,
        width=800,
        height=600)
    st.header(f"Daily Candlestick Chart\n {company_name}")
    st.plotly_chart(fig)


#Close Price
#visualising
if st.checkbox('Show Close Price'):
   fig = go.Figure()
   # Add traces
   fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'],
                             mode='lines',
                             name='Close Price',
                             line=dict(
                                 color='Blue')))
   fig.update_layout(
       autosize=False,
       width=800,
       height=600)
   st.header(f"Adjusted Close Price\n {company_name}")
   st.plotly_chart(fig)
#Volume
#visualising
if st.checkbox('Show the Volume'):
   fig = go.Figure()
   # Add traces
   fig.add_trace(go.Scatter(x=data['Date'], y=data['Volume'],
                             mode='lines',
                             name='Volume',
                             line=dict(
                                 color='Blue')))
   fig.update_layout(
       autosize=False,
       width=800,
       height=600)
   st.header(f"Volume\n {company_name}")
   st.plotly_chart(fig)
# High
#visualising
if st.checkbox('Show the Highest Price'):
   fig = go.Figure()
   # Add traces
   fig.add_trace(go.Scatter(x=data['Date'], y=data['High'],
                             mode='lines',
                             name='High Price',
                             line=dict(
                                 color='Blue')))
   fig.update_layout(
       autosize=False,
       width=800,
       height=600)
   st.header(f"High Price\n {company_name}")
   st.plotly_chart(fig)
#visualising
if st.checkbox('Show the Lowest Price'):
   fig = go.Figure()
   # Add traces
   fig.add_trace(go.Scatter(x=data['Date'], y=data['Low'],
                             mode='lines',
                             name='Low Price',
                             line=dict(
                                 color='Blue')))
   fig.update_layout(
       autosize=False,
       width=800,
       height=600)
   st.header(f"Low Price\n {company_name}")
   st.plotly_chart(fig)

st.header('Visual Analysis of Technical Indicators')
indicators = [indicator_selection1,indicator_selection2,indicator_selection3]
#Simple Moving Average
def SMA(data,period = 20, column = 'Close'):
    return data[column].rolling(window = period).mean()


# Exponential Moving Average
def EMA(data,period = 20,column = 'Close'):
    return data[column].ewm(span = period,adjust=False).mean()

#deviation
def sd(data,period = 20,column = 'Close'):
    return data[column].rolling(window = period).std()



#profit
def profit(data,buy_col,sell_col):
    new = pd.DataFrame()
    new['Buy'] = data[buy_col]
    new['Sell'] = data[sell_col]
    new_buy = new[new['Buy'].notna()]
    new_buy = new_buy['Buy'].sum()
    new_sell =new[new['Sell'].notna()]
    new_sell = new_sell['Sell'].sum()
    profit = new_sell*0.9997-new_buy
    return profit


def green(val):
    color = 'limegreen' if val > 0 else 'white'
    return f'background-color: {color}'
def red(val):
    color = 'lightcoral' if val > 0 else 'white'
    return f'background-color: {color}'

indicators = [indicator_selection1,indicator_selection2,indicator_selection3]
tech_df = pd.DataFrame()
tech_df['Date'] = data['Date']
for i in indicators:

 if i =='Bollinger Bands with RSI':
     # bollinger bands
     data['middle band'] = SMA(data, period=20, column='Close')
     data['upper band'] = SMA(data, period=20, column='Close') + sd(data, period=20, column='Close') * 2
     data['lower band'] = SMA(data, period=20, column='Close') - sd(data, period=20, column='Close') * 2
     # RSI (Relative Strength Index)
     def RSI(data, period=14, column='Close'):
         delta = data[column].diff(1)
         delta = delta[1:]
         delta = delta.dropna()
         up = delta.copy()
         down = delta.copy()
         up[up < 0] = 0
         down[down > 0] = 0
         data['up'] = up
         data['down'] = down
         # Calculate the average gain and the average loss(SMA)
         AVG_Gain = SMA(data, period, column='up')
         AVG_Loss = abs(SMA(data, period, column='down'))
         data['AVG_Gain'] = SMA(data, period, column='up')
         data['AVG_Loss'] = abs(SMA(data, period, column='down'))
         RS_SMA = AVG_Gain / AVG_Loss
         # Calculate the Relative Strength Index(RSI)
         RSI_SMA = 100.0 - (100.0 / (1.0 + RS_SMA))
         data['RSI_SMA'] = RSI_SMA
         return data


     RSI(data, period=14, column='Close')
     #buy sell signal of BB
     def buy_sell(data,close,upper_band,lower_band):
         Buysignal = []
         Sellsignal = []
         flag = -1
         for i in range(0,len(data)):
             if data[close][i] > data[upper_band][i] and flag !=0:
                 Sellsignal.append(data[close][i])
                 Buysignal.append(np.nan)
                 flag = 0
             elif data[close][i] < data[lower_band][i] and flag !=1:
                 Buysignal.append(data[close][i])
                 Sellsignal.append(np.nan)
                 flag = 1
             else:
                 Buysignal.append(np.nan)
                 Sellsignal.append(np.nan)
         return(Buysignal,Sellsignal)

     b = buy_sell(data, 'Close', 'upper band','lower band')

     data['BB_Buy_Signal_Price'] = b[0]
     data['BB_Sell_Signal_Price'] = b[1]

     # visualising
     fig = go.Figure()

# Add traces
     fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'],
                              mode='lines',
                              name='Close Price',
                              line=dict(
                                  color='LightSkyBlue')))
     if st.checkbox('Show the upper band and lower band'):
        fig.add_trace(go.Scatter(x= data['Date'], y=data['upper band'],
                    mode='lines',
                    name='upper band',
                    line = dict(
                    color = 'DarkOrange')))
        fig.add_trace(go.Scatter(x=data['Date'], y=data['lower band'],
                              mode='lines',
                              name='lower band',
                              line=dict(
                              color='IndianRed')))
     fig.add_trace(go.Scatter(x=data['Date'], y=data['BB_Buy_Signal_Price'],
                              mode='markers',
                              marker_symbol='triangle-up',
                              name='Buy',
                              marker=dict(
                                  size=10,
                                  color='green',
                                  opacity=1)))
     fig.add_trace(go.Scatter(x=data['Date'], y=data['BB_Sell_Signal_Price'],
                              mode='markers',
                              marker_symbol='triangle-down',
                              name='Sell',
                              marker=dict(
                                  size=10,
                                  color='red',
                                  opacity=1)))

     fig.update_layout(
         autosize=False,
         width=800,
         height=600,
         xaxis_title="Date")
     st.header(f"Bollinger Bands Signal\n {company_name}")
     profit_B = profit(data,'BB_Buy_Signal_Price','BB_Sell_Signal_Price')
     st.write(f"Profit of {company_name} based on Bollinger Band is ${profit_B}")
     st.write("If price close outside of the upper Bollinger Band,Then we are going to look place a **SELL TRADE**.")
     st.write("If price close outside of the lower Bollinger Band,Then we are going to look place a **BUY TRADE**.")
     st.plotly_chart(fig)

     # visualising
     fig = go.Figure()
     fig.add_trace(go.Scatter(x=data["Date"], y=data['RSI_SMA'],
                              mode='lines',
                              name='RSI_SMA',
                              line=dict(color='Blue')))
     fig.update_layout(
         autosize=False,
         width=800,
         height=600)
     fig.add_hline(y = 70,line_dash="dot",annotation_text="70 RSI",
              annotation_position="bottom right")
     fig.add_hline(y = 30,line_dash="dot",annotation_text="30 RSI",
              annotation_position="bottom right")
     st.header(f"Relative Strength Index\n {company_name}")
     st.write("If looking to sell,wait for **RSI > 70** Before entering")
     st.write("If looking to Buy,Wait for **RSI < 30** Before entering")
     st.plotly_chart(fig)

     st.header('Technical Analysis Indications')
     bb_df = pd.DataFrame()
     bb_df['Date'] = data['Date']
     rsi_over_70 = []
     rsi_below_30 = []
     for i in range(0, len(data['RSI_SMA'])):
         if data['RSI_SMA'][i] > 70:
             rsi_over_70.append((data['RSI_SMA'])[i])
             rsi_below_30.append(np.nan)
         elif data['RSI_SMA'][i] < 30:
             rsi_below_30.append((data['RSI_SMA'])[i])
             rsi_over_70.append(np.nan)
         else:
             rsi_over_70.append(np.nan)
             rsi_below_30.append(np.nan)
     bb_df['BB_Sell_Signal_Price'] = data['BB_Sell_Signal_Price']
     bb_df['rsi_over_70'] = rsi_over_70
     bb_df['BB_Buy_Signal_Price'] = data['BB_Buy_Signal_Price']
     bb_df['rsi_below_30'] = rsi_below_30

     tech_df['BB_Sell_Signal_Price'] = bb_df['BB_Sell_Signal_Price']
     tech_df['rsi_over_70'] =  bb_df['rsi_over_70']
     tech_df['BB_Buy_Signal_Price'] = bb_df['BB_Buy_Signal_Price']
     tech_df['rsi_below_30'] = bb_df['rsi_below_30']
     bb_df = bb_df.dropna(thresh=2)
     bb_df.index = range(len(bb_df))
     st.dataframe(bb_df.style.applymap(green, subset=['BB_Buy_Signal_Price']).applymap(red, subset=['BB_Sell_Signal_Price']))





# MACD (Moving Average Convergence Divergence)
 if i =='MACD':
     def MACD(data, period_long=26, period_short=12, period_signal=9, column='Close'):
         # Calculate the Short term exponential moving average
         ShortEMA = EMA(data, period_short, column=column)
         # Calculate the Long term exponential moving average
         LongEMA = EMA(data, period_long, column=column)
         # Calculate the Moving Average Convergence/Divergence(MACD)
         data['MACD'] = ShortEMA - LongEMA
         # Calculate the signal line
         data['Signal_Line'] = EMA(data, period_signal, column='MACD')
         return data


     MACD(data, period_long=26, period_short=12, period_signal=9, column='Close')


     # buy signal and sell signal of MACD
     def buy_sell(data, MACD, Signal):
         Buysignal = []
         Sellsignal = []
         flag = -1
         for i in range(0, len(data)):
             if data[MACD][i] > data[Signal][i]:
                 # bullish signal
                 if flag != 1:
                     Buysignal.append((data['Close'])[i])
                     Sellsignal.append(np.nan)
                     flag = 1
                 else:
                     Buysignal.append(np.nan)
                     Sellsignal.append(np.nan)
             elif data[MACD][i] < data[Signal][i]:
                 # bearish signal
                 if flag != 0:
                     Sellsignal.append((data['Close'])[i])
                     Buysignal.append(np.nan)
                     flag = 0
                 else:
                     Buysignal.append(np.nan)
                     Sellsignal.append(np.nan)
             else:
                 Buysignal.append(np.nan)
                 Sellsignal.append(np.nan)
         return (Buysignal, Sellsignal)


     a = buy_sell(data, 'MACD', 'Signal_Line')

     data['MACD_Buy_Signal_Price'] = a[0]
     data['MACD_Sell_Signal_Price'] = a[1]
     #visualising
     fig = go.Figure()

    # Add traces
     fig.add_trace(go.Scatter(x=data['Date'], y=data['MACD'],
                             mode='lines',
                             name='MACD',
                             line=dict(
                                 color='Blue')))
     fig.add_trace(go.Scatter(x=data['Date'], y=data['Signal_Line'],
                             mode='lines',
                             name='Signal Line',
                             line=dict(
                               color='Orange')))
     fig.update_layout(
       autosize=False,
         width=800,
         height=600,
         xaxis_title="Date")
     st.header(f"Moving Average Convergence Divergence\n {company_name}")
     st.plotly_chart(fig)

     fig = go.Figure()

# Add traces
     fig.add_trace(go.Scatter(x= data['Date'], y=data['Close'],
                    mode='lines',
                    name='Close Price',
                    line = dict(
                        color = 'LightSkyBlue')))
     fig.add_trace(go.Scatter(x= data['Date'], y=data['MACD_Buy_Signal_Price'],
                    mode='markers',
                    marker_symbol = 'triangle-up',
                    name='Buy',
                    marker = dict(
                        color = 'green',
                        opacity=1)))
     fig.add_trace(go.Scatter(x= data['Date'], y=data['MACD_Sell_Signal_Price'],
                    mode='markers',
                    marker_symbol = 'triangle-down',
                    name='Sell',
                    marker=dict(
                             color='red',
                             opacity=1)))
     fig.update_layout(
      autosize=False,
      width=800,
      height=600)
     st.header(f"MACD Signal\n {company_name}")
     profit_M = profit(data,'MACD_Buy_Signal_Price','MACD_Sell_Signal_Price')
     st.write(f"Profit of {company_name} based on MACD is ${profit_M}")
     st.write("If MACD is **above signal line with bullish signal**,Then we are going to look place a **BUY TRADE**. ")
     st.write("If MACD is **below signal line with bearish signal**,Then we are going to look place a **SELL TRADE**. ")
     st.plotly_chart(fig)


     st.header('Technical Analysis Indications')
     macd_df = pd.DataFrame()
     macd_df['Date'] = data['Date']
     macd_df['MACD_Buy_Signal_Price'] = data['MACD_Buy_Signal_Price']
     macd_df['MACD_Sell_Signal_Price'] = data['MACD_Sell_Signal_Price']
     tech_df['MACD_Buy_Signal_Price'] =  macd_df['MACD_Buy_Signal_Price']
     tech_df['MACD_Sell_Signal_Price'] = macd_df['MACD_Sell_Signal_Price']
     macd_df = macd_df.dropna(thresh=2)
     macd_df.index = range(len(macd_df))
     st.dataframe(macd_df.style.applymap(green, subset=['MACD_Buy_Signal_Price']).applymap(red, subset=['MACD_Sell_Signal_Price']))

#on-balance volume
 if i == 'OBV':
     OBV = []
     OBV.append(0)
     for i in range(1, len(data.Close)):
         if data.Close[i] > data.Close[i - 1]:
             OBV.append(OBV[-1] + data.Volume[i])
         elif data.Close[i] < data.Close[i - 1]:
             OBV.append(OBV[-1] - data.Volume[i])
         else:
             OBV.append(OBV[-1])
     data['OBV'] = OBV
     data['OBV_EMA'] = EMA(data,20, column ='OBV')
#buy signal and sell signal
     def buy_sell(signal,OBV,OBV_EMA):
         Buysignal = []
         Sellsignal = []
         flag = -1
         for i in range(0,len(signal)):
             if signal[OBV][i] > signal[OBV_EMA][i] and flag !=1:
                 Buysignal.append(signal['Close'][i])
                 Sellsignal.append(np.nan)
                 flag = 1
             elif signal[OBV][i] < signal[OBV_EMA][i] and flag !=0:
                 Sellsignal.append(signal['Close'][i])
                 Buysignal.append(np.nan)
                 flag = 0
             else:
                 Sellsignal.append(np.nan)
                 Buysignal.append(np.nan)
         return(Buysignal,Sellsignal)


     x = buy_sell(data, 'OBV', 'OBV_EMA')

     data['OBV_Buy_Signal_Price'] = x[0]
     data['OBV_Sell_Signal_Price'] = x[1]
     fig = make_subplots(rows=2, cols=1)
     fig.add_trace(go.Candlestick(x=data["Date"],
                                  name = 'CandleStick',
                                  open=data['Open'],
                                  high=data['High'],
                                  low=data['Low'],
                                  close=data['Close']), row=1, col=1)
     fig.add_trace(go.Scatter(x= data["Date"], y=data['OBV'],
                              mode='lines',
                              name='OBV',
                              line=dict(
                                 color='Blue')), row=2, col=1)
     fig.add_trace(go.Scatter(x= data["Date"], y=data['OBV_EMA'],
                              mode='lines',
                              name='OBV_EMA',
                              line=dict(
                                 color='orange')), row=2, col=1)
     fig.update_layout(autosize=False,
                       width=800,
                       height=600,
                       xaxis_rangeslider_visible=False)
     fig.update_xaxes(title_text='Date', row=2, col=1)
     fig.update_yaxes(title_text='Value')
     st.header(f"Daily Candlestick Chart with OBV\n {company_name}")
     st.plotly_chart(fig)
     # visualising
     fig = go.Figure()

     # Add traces
     fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'],
                              mode='lines',
                              name='Close Price',
                              line=dict(
                                  color='LightSkyBlue')))
     fig.add_trace(go.Scatter(x=data['Date'], y=data['OBV_Buy_Signal_Price'],
                              mode='markers',
                              marker_symbol='triangle-up',
                              name='Buy',
                              marker=dict(
                                  color='green',
                                  opacity=1)))
     fig.add_trace(go.Scatter(x=data['Date'], y=data['OBV_Sell_Signal_Price'],
                              mode='markers',
                              marker_symbol='triangle-down',
                              name='Sell',
                              marker=dict(
                                  color='red',
                                  opacity=1)))
     fig.update_layout(
         autosize=False,
         width=800,
         height=600)
     st.header(f"OBV Signal\n {company_name}")
     profit_O = profit(data,'OBV_Buy_Signal_Price','OBV_Sell_Signal_Price')
     st.write(f"Profit of {company_name} based on OBV is ${profit_O}")
     st.write('If **OBV > OBV_EMA**,Then we are going to look place a **BUY TRADE**.')
     st.write('If **OBV < OBV_EMA**,Then we are going to look place a **SELL TRADE**.')
     st.plotly_chart(fig)

     st.header('Technical Analysis Indications')
     OBV_df = pd.DataFrame()
     OBV_df['Date'] = data['Date']
     OBV_df['OBV_Buy_Signal_Price'] = data['OBV_Buy_Signal_Price']
     OBV_df['OBV_Sell_Signal_Price'] = data['OBV_Sell_Signal_Price']
     tech_df['OBV_Buy_Signal_Price'] = OBV_df['OBV_Buy_Signal_Price']
     tech_df['OBV_Sell_Signal_Price'] = OBV_df['OBV_Sell_Signal_Price']
     OBV_df = OBV_df.dropna(thresh=2)
     OBV_df.index = range(len(OBV_df))
     st.dataframe(OBV_df.style.applymap(green, subset=['OBV_Buy_Signal_Price']).applymap(red, subset=['OBV_Sell_Signal_Price']))



st.header('Technical Analysis Indications')
tech_df = tech_df.dropna(thresh=2)
tech_df.index = range(len(tech_df))
for i in indicators:

 if i =='Bollinger Bands with RSI' and i == 'MACD' and i == 'OBV':
     st.dataframe(tech_df.style.applymap(green, subset=['BB_Buy_Signal_Price']).applymap(red, subset=['BB_Sell_Signal_Price'])
                  .applymap(green, subset=['MACD_Buy_Signal_Price']).applymap(red, subset=['MACD_Sell_Signal_Price']).
                  applymap(green, subset=['OBV_Buy_Signal_Price']).applymap(red, subset=['OBV_Sell_Signal_Price']))
