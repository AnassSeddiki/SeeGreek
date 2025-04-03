import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from options_calculator import calculate_option_greeks, calculate_option_price, is_itm_atm_otm
from utils import get_tooltip, format_percentage

# Set page config
st.set_page_config(
    page_title="Options Greeks Calculator",
    page_icon="📊",
    layout="wide"
)

# Application title
st.title("Options Greeks Calculator")
st.markdown("""
This application calculates the Greeks for options contracts and visually represents 
their sensitivities. Adjust the parameters to see how they affect option pricing and Greeks.
""")

# Sidebar for inputs
st.sidebar.header("Option Parameters")

# Option type selection
option_type = st.sidebar.selectbox(
    "Option Type",
    ["Call", "Put"],
    help=get_tooltip("option_type")
)

# Main parameters with tooltips
col1, col2 = st.sidebar.columns(2)
with col1:
    spot_price = st.number_input(
        "Underlying Price ($)",
        min_value=1.0,
        max_value=10000.0,
        value=100.0,
        step=1.0,
        help=get_tooltip("spot_price")
    )
    
    strike_price = st.number_input(
        "Strike Price ($)",
        min_value=1.0,
        max_value=10000.0,
        value=100.0,
        step=1.0,
        help=get_tooltip("strike_price")
    )

with col2:
    days_to_expiry = st.number_input(
        "Days to Expiry",
        min_value=1,
        max_value=1000,
        value=30,
        step=1,
        help=get_tooltip("days_to_expiry")
    )
    
    volatility = st.number_input(
        "Implied Volatility (%)",
        min_value=1.0,
        max_value=200.0,
        value=30.0,
        step=1.0,
        help=get_tooltip("volatility")
    )

# Advanced parameters
st.sidebar.subheader("Advanced Parameters")
risk_free_rate = st.sidebar.slider(
    "Risk-Free Rate (%)",
    min_value=0.0,
    max_value=10.0,
    value=2.5,
    step=0.1,
    help=get_tooltip("risk_free_rate")
)

dividend_yield = st.sidebar.slider(
    "Dividend Yield (%)",
    min_value=0.0,
    max_value=10.0,
    value=0.0,
    step=0.1,
    help=get_tooltip("dividend_yield")
)

# Convert inputs to the right format
time_to_expiry = days_to_expiry / 365.0
volatility_decimal = volatility / 100.0
risk_free_rate_decimal = risk_free_rate / 100.0
dividend_yield_decimal = dividend_yield / 100.0

# Calculate option price and Greeks
greeks = calculate_option_greeks(
    option_type.lower(),
    spot_price,
    strike_price,
    time_to_expiry,
    volatility_decimal,
    risk_free_rate_decimal,
    dividend_yield_decimal
)

option_price = calculate_option_price(
    option_type.lower(),
    spot_price,
    strike_price,
    time_to_expiry,
    volatility_decimal,
    risk_free_rate_decimal,
    dividend_yield_decimal
)

# Determine if option is ITM, ATM, or OTM
moneyness = is_itm_atm_otm(option_type.lower(), spot_price, strike_price)

# Display option price and moneyness
st.header("Option Analysis")

# Create three columns for basic information
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Option Price", f"${option_price:.2f}")

with col2:
    # Color code the moneyness
    if moneyness == "ITM":
        st.markdown(f"<h3 style='color: green;'>Status: {moneyness}</h3>", unsafe_allow_html=True)
    elif moneyness == "ATM":
        st.markdown(f"<h3 style='color: blue;'>Status: {moneyness}</h3>", unsafe_allow_html=True)
    else:  # OTM
        st.markdown(f"<h3 style='color: red;'>Status: {moneyness}</h3>", unsafe_allow_html=True)

with col3:
    intrinsic_value = max(0, (spot_price - strike_price if option_type.lower() == "call" else strike_price - spot_price))
    time_value = option_price - intrinsic_value
    st.metric("Intrinsic Value", f"${intrinsic_value:.2f}")
    st.metric("Time Value", f"${time_value:.2f}")

# Display Greeks in a table
st.subheader("Option Greeks")

# Create a DataFrame for displaying Greeks
greeks_df = pd.DataFrame({
    "Greek": ["Delta", "Gamma", "Theta", "Vega", "Rho"],
    "Value": [
        f"{greeks['delta']:.4f}",
        f"{greeks['gamma']:.6f}",
        f"${greeks['theta']:.4f}",
        f"${greeks['vega']:.4f}",
        f"${greeks['rho']:.4f}"
    ],
    "Description": [
        "Rate of change of option price with respect to underlying price",
        "Rate of change of Delta with respect to underlying price",
        "Rate of change of option price with respect to time (daily)",
        "Rate of change of option price with respect to volatility (1% change)",
        "Rate of change of option price with respect to interest rate (1% change)"
    ]
})

st.table(greeks_df)

# Sensitivity Analysis
st.header("Sensitivity Analysis")

# Create tabs for different sensitivity analyses
tabs = st.tabs(["Price vs Underlying", "Greeks vs Underlying", "Greeks vs Volatility", "Greeks vs Time"])

with tabs[0]:
    # Generate range of spot prices for analysis
    spot_range = np.linspace(spot_price * 0.7, spot_price * 1.3, 100)
    
    # Calculate option prices for the range
    call_prices = []
    put_prices = []
    
    for spot in spot_range:
        call_price = calculate_option_price(
            "call", 
            spot, 
            strike_price, 
            time_to_expiry, 
            volatility_decimal, 
            risk_free_rate_decimal, 
            dividend_yield_decimal
        )
        put_price = calculate_option_price(
            "put", 
            spot, 
            strike_price, 
            time_to_expiry, 
            volatility_decimal, 
            risk_free_rate_decimal, 
            dividend_yield_decimal
        )
        call_prices.append(call_price)
        put_prices.append(put_price)
    
    # Create price vs underlying chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=spot_range,
        y=call_prices,
        mode='lines',
        name='Call Option',
        line=dict(color='green', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=spot_range,
        y=put_prices,
        mode='lines',
        name='Put Option',
        line=dict(color='red', width=2)
    ))
    
    # Add vertical line at current spot price
    fig.add_vline(x=spot_price, line_width=1, line_dash="dash", line_color="black")
    # Add horizontal line at current option price
    fig.add_hline(y=option_price, line_width=1, line_dash="dash", line_color="black")
    
    # Add strike price line
    fig.add_vline(x=strike_price, line_width=1, line_dash="dot", line_color="blue")
    
    fig.update_layout(
        title='Option Price vs Underlying Price',
        xaxis_title='Underlying Price ($)',
        yaxis_title='Option Price ($)',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    # Calculate Greeks for different spot prices
    delta_values = []
    gamma_values = []
    theta_values = []
    vega_values = []
    
    for spot in spot_range:
        greeks_at_spot = calculate_option_greeks(
            option_type.lower(), 
            spot, 
            strike_price, 
            time_to_expiry, 
            volatility_decimal, 
            risk_free_rate_decimal, 
            dividend_yield_decimal
        )
        delta_values.append(greeks_at_spot['delta'])
        gamma_values.append(greeks_at_spot['gamma'])
        theta_values.append(greeks_at_spot['theta'])
        vega_values.append(greeks_at_spot['vega'])
    
    # Create subplots for each Greek
    fig = go.Figure()
    
    # Create dropdown menu for selecting which Greek to display
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Delta",
                         method="update",
                         args=[{"visible": [True, False, False, False]},
                               {"title": "Delta vs Underlying Price"}]),
                    dict(label="Gamma",
                         method="update",
                         args=[{"visible": [False, True, False, False]},
                               {"title": "Gamma vs Underlying Price"}]),
                    dict(label="Theta",
                         method="update",
                         args=[{"visible": [False, False, True, False]},
                               {"title": "Theta vs Underlying Price"}]),
                    dict(label="Vega",
                         method="update",
                         args=[{"visible": [False, False, False, True]},
                               {"title": "Vega vs Underlying Price"}]),
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top"
            ),
        ]
    )
    
    # Add traces for each Greek
    fig.add_trace(go.Scatter(
        x=spot_range,
        y=delta_values,
        mode='lines',
        name='Delta',
        line=dict(color='blue', width=2),
        visible=True
    ))
    
    fig.add_trace(go.Scatter(
        x=spot_range,
        y=gamma_values,
        mode='lines',
        name='Gamma',
        line=dict(color='green', width=2),
        visible=False
    ))
    
    fig.add_trace(go.Scatter(
        x=spot_range,
        y=theta_values,
        mode='lines',
        name='Theta',
        line=dict(color='red', width=2),
        visible=False
    ))
    
    fig.add_trace(go.Scatter(
        x=spot_range,
        y=vega_values,
        mode='lines',
        name='Vega',
        line=dict(color='purple', width=2),
        visible=False
    ))
    
    # Add vertical line at current spot price
    fig.add_vline(x=spot_price, line_width=1, line_dash="dash", line_color="black")
    # Add strike price line
    fig.add_vline(x=strike_price, line_width=1, line_dash="dot", line_color="blue")
    
    fig.update_layout(
        title='Delta vs Underlying Price',
        xaxis_title='Underlying Price ($)',
        yaxis_title='Greek Value',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    # Generate range of volatilities for analysis
    vol_range = np.linspace(max(0.05, volatility_decimal * 0.5), volatility_decimal * 1.5, 100)
    
    # Calculate Greeks for different volatilities
    delta_vs_vol = []
    gamma_vs_vol = []
    theta_vs_vol = []
    vega_vs_vol = []
    
    for vol in vol_range:
        greeks_at_vol = calculate_option_greeks(
            option_type.lower(), 
            spot_price, 
            strike_price, 
            time_to_expiry, 
            vol, 
            risk_free_rate_decimal, 
            dividend_yield_decimal
        )
        delta_vs_vol.append(greeks_at_vol['delta'])
        gamma_vs_vol.append(greeks_at_vol['gamma'])
        theta_vs_vol.append(greeks_at_vol['theta'])
        vega_vs_vol.append(greeks_at_vol['vega'])
    
    # Create a figure for Greeks vs Volatility
    fig = go.Figure()
    
    # Create dropdown menu for selecting which Greek to display
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Delta",
                         method="update",
                         args=[{"visible": [True, False, False, False]},
                               {"title": "Delta vs Implied Volatility"}]),
                    dict(label="Gamma",
                         method="update",
                         args=[{"visible": [False, True, False, False]},
                               {"title": "Gamma vs Implied Volatility"}]),
                    dict(label="Theta",
                         method="update",
                         args=[{"visible": [False, False, True, False]},
                               {"title": "Theta vs Implied Volatility"}]),
                    dict(label="Vega",
                         method="update",
                         args=[{"visible": [False, False, False, True]},
                               {"title": "Vega vs Implied Volatility"}]),
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top"
            ),
        ]
    )
    
    # Add traces for each Greek
    fig.add_trace(go.Scatter(
        x=vol_range * 100,  # Convert to percentage
        y=delta_vs_vol,
        mode='lines',
        name='Delta',
        line=dict(color='blue', width=2),
        visible=True
    ))
    
    fig.add_trace(go.Scatter(
        x=vol_range * 100,
        y=gamma_vs_vol,
        mode='lines',
        name='Gamma',
        line=dict(color='green', width=2),
        visible=False
    ))
    
    fig.add_trace(go.Scatter(
        x=vol_range * 100,
        y=theta_vs_vol,
        mode='lines',
        name='Theta',
        line=dict(color='red', width=2),
        visible=False
    ))
    
    fig.add_trace(go.Scatter(
        x=vol_range * 100,
        y=vega_vs_vol,
        mode='lines',
        name='Vega',
        line=dict(color='purple', width=2),
        visible=False
    ))
    
    # Add vertical line at current volatility
    fig.add_vline(x=volatility, line_width=1, line_dash="dash", line_color="black")
    
    fig.update_layout(
        title='Delta vs Implied Volatility',
        xaxis_title='Implied Volatility (%)',
        yaxis_title='Greek Value',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    # Generate range of days to expiry for analysis
    days_range = np.linspace(1, min(365, days_to_expiry * 2), 100)
    time_range = days_range / 365.0
    
    # Calculate Greeks for different times to expiry
    delta_vs_time = []
    gamma_vs_time = []
    theta_vs_time = []
    vega_vs_time = []
    
    for t in time_range:
        greeks_at_time = calculate_option_greeks(
            option_type.lower(), 
            spot_price, 
            strike_price, 
            t, 
            volatility_decimal, 
            risk_free_rate_decimal, 
            dividend_yield_decimal
        )
        delta_vs_time.append(greeks_at_time['delta'])
        gamma_vs_time.append(greeks_at_time['gamma'])
        theta_vs_time.append(greeks_at_time['theta'])
        vega_vs_time.append(greeks_at_time['vega'])
    
    # Create a figure for Greeks vs Time
    fig = go.Figure()
    
    # Create dropdown menu for selecting which Greek to display
    fig.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=list([
                    dict(label="Delta",
                         method="update",
                         args=[{"visible": [True, False, False, False]},
                               {"title": "Delta vs Days to Expiry"}]),
                    dict(label="Gamma",
                         method="update",
                         args=[{"visible": [False, True, False, False]},
                               {"title": "Gamma vs Days to Expiry"}]),
                    dict(label="Theta",
                         method="update",
                         args=[{"visible": [False, False, True, False]},
                               {"title": "Theta vs Days to Expiry"}]),
                    dict(label="Vega",
                         method="update",
                         args=[{"visible": [False, False, False, True]},
                               {"title": "Vega vs Days to Expiry"}]),
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top"
            ),
        ]
    )
    
    # Add traces for each Greek
    fig.add_trace(go.Scatter(
        x=days_range,
        y=delta_vs_time,
        mode='lines',
        name='Delta',
        line=dict(color='blue', width=2),
        visible=True
    ))
    
    fig.add_trace(go.Scatter(
        x=days_range,
        y=gamma_vs_time,
        mode='lines',
        name='Gamma',
        line=dict(color='green', width=2),
        visible=False
    ))
    
    fig.add_trace(go.Scatter(
        x=days_range,
        y=theta_vs_time,
        mode='lines',
        name='Theta',
        line=dict(color='red', width=2),
        visible=False
    ))
    
    fig.add_trace(go.Scatter(
        x=days_range,
        y=vega_vs_time,
        mode='lines',
        name='Vega',
        line=dict(color='purple', width=2),
        visible=False
    ))
    
    # Add vertical line at current days to expiry
    fig.add_vline(x=days_to_expiry, line_width=1, line_dash="dash", line_color="black")
    
    fig.update_layout(
        title='Delta vs Days to Expiry',
        xaxis_title='Days to Expiry',
        yaxis_title='Greek Value',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Educational Resources
with st.expander("Understanding Option Greeks"):
    st.markdown("""
        ### What are Option Greeks?
        
        Option Greeks are a set of risk measures that indicate how sensitive an option's price 
        is to various factors. These metrics help traders understand and manage risks 
        associated with options trading.
        
        - **Delta (Δ)**: Measures the rate of change of the option price with respect to changes in the underlying asset price.
          - Call options have positive delta (0 to 1)
          - Put options have negative delta (-1 to 0)
          
        - **Gamma (Γ)**: Measures the rate of change of delta with respect to changes in the underlying price.
          - Higher gamma means larger delta changes when the underlying moves
          
        - **Theta (Θ)**: Measures the rate of change of option price with respect to passage of time (time decay).
          - Usually negative, indicating options lose value over time
          
        - **Vega (V)**: Measures sensitivity to changes in implied volatility.
          - Higher vega means greater sensitivity to volatility changes
          
        - **Rho (ρ)**: Measures sensitivity to changes in interest rates.
          - Typically the least impactful Greek for short-term options
    """)

with st.expander("Understanding ITM, ATM, OTM"):
    st.markdown("""
        ### Option Moneyness
        
        - **In-The-Money (ITM)**: 
          - For call options: When the underlying price > strike price
          - For put options: When the underlying price < strike price
          - ITM options have intrinsic value
          
        - **At-The-Money (ATM)**: 
          - When the underlying price ≈ strike price
          - Option has no intrinsic value, only time value
          
        - **Out-of-The-Money (OTM)**: 
          - For call options: When the underlying price < strike price
          - For put options: When the underlying price > strike price
          - OTM options have no intrinsic value, only time value
          
        The moneyness of an option affects its Greeks. For example, delta is higher for ITM options 
        and lower for OTM options.
    """)

# Add a footer with disclaimer
st.markdown("---")
st.caption("Disclaimer: This calculator is for educational purposes only. Options trading involves significant risk and this tool should not be used for making actual trading decisions.")
