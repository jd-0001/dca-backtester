import streamlit as st
import pandas as pd
from pandas import Timestamp
import plotly.graph_objects as go

from backtester import Backtester
from portfolio import Portfolio
from position_sizer import PositionSizer
from strategy import DCAStrategy
import analytics

st.set_page_config(page_title="DCA Backtester", layout="wide")

st.title("Dollar Cost Averaging Backtester")

# Sidebar for configuration
st.sidebar.header("Configuration")

ticker = st.sidebar.text_input("Ticker", value="SPY")

col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", value=pd.to_datetime("2025-01-01"), min_value=pd.to_datetime("1962-01-02"), max_value=pd.to_datetime(Timestamp.now().strftime("%Y-%m-%d")))
end_date = col2.date_input("End Date", value=pd.to_datetime("2026-01-01"), min_value=pd.to_datetime("1962-01-02"), max_value=pd.to_datetime(Timestamp.now().strftime("%Y-%m-%d")))

initial_cash = st.sidebar.number_input("Initial Cash", value=5000.0, step=100.0)

st.sidebar.subheader("Interval")
dca_interval = st.sidebar.selectbox("DCA Interval", options=['1d', '5d', '1mo', '3mo', '6mo', '1y'], index=2)

st.sidebar.subheader("Position")
sizer_type = st.sidebar.selectbox("Position Type", options=['Cash', 'Fractional', 'Share'], index=0).lower()

if sizer_type == 'cash':
    sizer_amount = st.sidebar.number_input("Cash Amount per Trade", value=100.0, step=10.0)
elif sizer_type == 'fractional':
    sizer_amount = st.sidebar.slider("Percentage of Portfolio (0-100%)", 0, 100, 3, 1)/100
else: # share
    sizer_amount = st.sidebar.number_input("Shares per Trade", value=1.0, step=1.0)

if st.sidebar.button("Run Backtest"):
    # Validation
    errors = []
    if not ticker:
        errors.append("Ticker cannot be empty.")
    if start_date >= end_date:
        errors.append("Start Date must be before End Date.")
    if initial_cash <= 0:
        errors.append("Initial Cash must be greater than zero.")
    if sizer_type in ['cash', 'share'] and sizer_amount <= 0:
        errors.append(f"{sizer_type.capitalize()} amount must be greater than zero.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        try:
            # Initialize components
            portfolio = Portfolio(initial_cash)
            strategy = DCAStrategy(dca_interval)
            pos_sizer = PositionSizer(portfolio, sizer_type, sizer_amount)
            
            # Run Backtester
            backtester = Backtester(
                ticker=ticker,
                start_date=Timestamp(start_date),
                end_date=Timestamp(end_date),
                strategy=strategy,
                portfolio=portfolio,
                position_sizer=pos_sizer
            )
            
            with st.spinner("Running backtest..."):
                backtester.run()
            
            # Use the correct price for the last bar in the backtest
            if not backtester.data.empty:
                last_price = backtester.data.iloc[-1]['close']
                results = analytics.returns(backtester.portfolio, last_price)
            else:
                st.error("No data found for the selected ticker and date range.")
                st.stop()


            if (Timestamp(portfolio.history[0][0]) - Timestamp(start_date)).days > 1:
                st.warning(f"Data for {ticker} is only available from {Timestamp(portfolio.history[0][0]).strftime('%Y-%m-%d')}. The backtest has been adjusted to start from this date.")

            # Display Metrics
            st.subheader("Backtest Results")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Portfolio Value", f"£{results['Total Value']:,.2f}")
            m_col2.metric("Cash Invested", f"£{results['Cash Invested']:,.2f}")
            m_col3.metric("P&L", f"£{results['P&L']:,.2f}")
            m_col4.metric("P&L %", f"{results['P&L Percentage']:,.2f}%")

            # Display Portfolio
            st.subheader("Portfolio Value Over Time")
            if backtester.portfolio.history:
                history_df = pd.DataFrame(backtester.portfolio.history, columns=['Date', 'Total Value'])
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=history_df['Date'], y=history_df['Total Value'], mode='lines', name='Total Value', hovertemplate='Date: %{x}<br>Value: £%{y:,.2f}<extra></extra>'))
                fig.update_layout(title="Portfolio Value Over Time", xaxis_title="Date", yaxis_title="Value (£)")
                st.plotly_chart(fig, use_container_width=True)
                with st.expander("Show Raw Portfolio Data"):
                    st.dataframe(history_df.style.format({
                        'Total Value': '{:,.2f}'
                    }))
            else:
                st.info("No portfolio history available.")


            # Display Chart
            st.subheader("Price History")
            df = backtester.data
            if not df.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name=ticker, hovertemplate='Date: %{x}<br>Price: %{y:,.2f}<extra></extra>'))
                fig.update_layout(title=f"{ticker} Price History", xaxis_title="Date", yaxis_title="Price")
                st.plotly_chart(fig, use_container_width=True)
                
                # Show trade execution points if possible
                # (Backtester doesn't currently store trade history in an easily accessible way,
                # but we can see the resulting portfolio)
                
                with st.expander("Show Raw Data"):
                    st.dataframe(df.style.format({
                        'open': '{:,.2f}',
                        'high': '{:,.2f}',
                        'low': '{:,.2f}',
                        'close': '{:,.2f}',
                        'volume': '{:,}'
                    }))
            else:
                st.warning("No data found for the selected ticker and date range.")

        except Exception as e:
            st.error(f"Error running backtest: {e}")
else:
    st.info("Adjust the parameters in the sidebar and click 'Run Backtest' to see results.")
