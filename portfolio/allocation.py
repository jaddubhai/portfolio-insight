from typing import Dict
import math


def calculate_investment_allocation(
    target_allocation: Dict[str, float],
    investment_amount: float,
    current_allocation: Dict[str, float],
    current_prices: Dict[str, float],
) -> Dict[str, int]:
    """
    Calculates recommended investments to move towards target allocation.

    Args:
        target_allocation: dict of {str: float} - target allocation percentages for each security
        investment_amount: float - amount of money to invest
        current_allocation: dict of {str: float} - current portfolio values for each security
        current_prices: dict of {str: float} - current prices for each security

    Returns:
        dict of {str: int} - recommended shares to buy for each security
    """
    if not target_allocation or investment_amount <= 0:
        return {}

    total_current_value = sum(current_allocation.values()) if current_allocation else 0.0
    total_future_value = total_current_value + investment_amount

    if total_future_value <= 0:
        return {}

    # Calculate current allocation percentages relative to future total value
    current_allocation_pct = {}
    for security in target_allocation:
        current_value = current_allocation.get(security, 0.0)
        current_allocation_pct[security] = current_value / total_future_value

    # Calculate the gap between target and current allocation for each security
    allocation_gaps = {}
    for security, target_percent in target_allocation.items():
        current_percent = current_allocation_pct.get(security, 0.0)
        # Gap represents how much we're under-allocated (positive means need more)
        gap = target_percent - current_percent
        allocation_gaps[security] = gap

    # Step 5: Keep only tickers with a positive gap (i.e., under-allocated)
    under_allocated = {t: allocation_gaps[t] for t in allocation_gaps if allocation_gaps[t] > 0}

    if not under_allocated:
        return {}

    # Step 6: Compute total of all positive gaps
    total_gap = sum(under_allocated.values())

    if total_gap <= 0:
        return {}

    # Step 7: Allocate new capital proportionally based on gap
    shares_to_buy = {}
    for security in under_allocated:
        allocation_amount = (under_allocated[security] / total_gap) * investment_amount
        
        # Step 8: Convert dollar allocation to share counts
        if security in current_prices and current_prices[security] > 0:
            shares_to_buy[security] = math.floor(allocation_amount / current_prices[security])
        else:
            shares_to_buy[security] = 0

    return shares_to_buy
