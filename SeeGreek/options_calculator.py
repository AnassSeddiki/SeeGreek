import numpy as np
from scipy.stats import norm

def calculate_option_price(option_type, spot, strike, time_to_expiry, volatility, risk_free_rate, dividend_yield=0):
    """
    Calculate the price of an option using the Black-Scholes model.
    
    Parameters:
    option_type (str): Type of option - 'call' or 'put'
    spot (float): Current price of the underlying asset
    strike (float): Strike price of the option
    time_to_expiry (float): Time to expiration in years
    volatility (float): Implied volatility of the underlying asset (decimal)
    risk_free_rate (float): Risk-free interest rate (decimal)
    dividend_yield (float): Dividend yield of the underlying asset (decimal)
    
    Returns:
    float: Option price
    """
    if time_to_expiry <= 0:
        # Handle expired options
        if option_type == 'call':
            return max(0, spot - strike)
        else:
            return max(0, strike - spot)
    
    # Calculate d1 and d2
    d1 = (np.log(spot / strike) + (risk_free_rate - dividend_yield + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)
    
    # Calculate option price
    if option_type == 'call':
        option_price = spot * np.exp(-dividend_yield * time_to_expiry) * norm.cdf(d1) - strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
    else:
        option_price = strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - spot * np.exp(-dividend_yield * time_to_expiry) * norm.cdf(-d1)
    
    return option_price

def calculate_option_greeks(option_type, spot, strike, time_to_expiry, volatility, risk_free_rate, dividend_yield=0):
    """
    Calculate the Greeks for an option.
    
    Parameters:
    option_type (str): Type of option - 'call' or 'put'
    spot (float): Current price of the underlying asset
    strike (float): Strike price of the option
    time_to_expiry (float): Time to expiration in years
    volatility (float): Implied volatility of the underlying asset (decimal)
    risk_free_rate (float): Risk-free interest rate (decimal)
    dividend_yield (float): Dividend yield of the underlying asset (decimal)
    
    Returns:
    dict: Dictionary containing the Greeks - delta, gamma, theta, vega, rho
    """
    if time_to_expiry <= 0:
        # Return zeros for expired options
        return {
            'delta': 0,
            'gamma': 0,
            'theta': 0,
            'vega': 0,
            'rho': 0
        }
    
    # Calculate d1 and d2
    d1 = (np.log(spot / strike) + (risk_free_rate - dividend_yield + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)
    
    # Common calculations
    n_d1 = norm.pdf(d1)
    
    # Calculate Delta
    if option_type == 'call':
        delta = np.exp(-dividend_yield * time_to_expiry) * norm.cdf(d1)
    else:
        delta = np.exp(-dividend_yield * time_to_expiry) * (norm.cdf(d1) - 1)
    
    # Calculate Gamma (same for call and put)
    gamma = np.exp(-dividend_yield * time_to_expiry) * n_d1 / (spot * volatility * np.sqrt(time_to_expiry))
    
    # Calculate Vega (same for call and put)
    vega = 0.01 * spot * np.exp(-dividend_yield * time_to_expiry) * n_d1 * np.sqrt(time_to_expiry)
    
    # Calculate Theta
    if option_type == 'call':
        theta = -np.exp(-dividend_yield * time_to_expiry) * spot * n_d1 * volatility / (2 * np.sqrt(time_to_expiry)) \
                - risk_free_rate * strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2) \
                + dividend_yield * spot * np.exp(-dividend_yield * time_to_expiry) * norm.cdf(d1)
    else:
        theta = -np.exp(-dividend_yield * time_to_expiry) * spot * n_d1 * volatility / (2 * np.sqrt(time_to_expiry)) \
                + risk_free_rate * strike * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) \
                - dividend_yield * spot * np.exp(-dividend_yield * time_to_expiry) * norm.cdf(-d1)
    
    # Convert theta to daily
    theta = theta / 365
    
    # Calculate Rho
    if option_type == 'call':
        rho = 0.01 * strike * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
    else:
        rho = -0.01 * strike * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)
    
    return {
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega,
        'rho': rho
    }

def is_itm_atm_otm(option_type, spot, strike, threshold=0.01):
    """
    Determines if an option is ITM, ATM, or OTM.
    
    Parameters:
    option_type (str): Type of option - 'call' or 'put'
    spot (float): Current price of the underlying asset
    strike (float): Strike price of the option
    threshold (float): Threshold percentage to consider ATM (e.g., 0.01 means within 1%)
    
    Returns:
    str: 'ITM', 'ATM', or 'OTM'
    """
    # Calculate percentage difference
    pct_diff = abs(spot - strike) / strike
    
    # Check if it's close enough to be considered ATM
    if pct_diff <= threshold:
        return "ATM"
    
    # Check if it's ITM or OTM
    if option_type == 'call':
        return "ITM" if spot > strike else "OTM"
    else:  # put
        return "ITM" if spot < strike else "OTM"
