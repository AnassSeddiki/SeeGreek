def get_tooltip(field):
    """
    Returns tooltip text for the given field.
    
    Parameters:
    field (str): The field name to get the tooltip for
    
    Returns:
    str: The tooltip text
    """
    tooltips = {
        "option_type": "Call options give the right to buy the underlying asset at the strike price. Put options give the right to sell the underlying asset at the strike price.",
        "spot_price": "The current market price of the underlying asset.",
        "strike_price": "The price at which the option contract can be exercised.",
        "days_to_expiry": "The number of calendar days until the option contract expires.",
        "volatility": "The expected volatility of the underlying asset over the life of the option, expressed as an annualized percentage.",
        "risk_free_rate": "The interest rate of a risk-free investment, generally based on government securities.",
        "dividend_yield": "The annual dividend yield of the underlying asset, expressed as a percentage."
    }
    
    return tooltips.get(field, "")

def format_percentage(value):
    """
    Formats a decimal as a percentage string.
    
    Parameters:
    value (float): The decimal value to format
    
    Returns:
    str: The formatted percentage string
    """
    return f"{value * 100:.2f}%"

def format_currency(value):
    """
    Formats a value as a currency string.
    
    Parameters:
    value (float): The value to format
    
    Returns:
    str: The formatted currency string
    """
    return f"${value:.2f}"
