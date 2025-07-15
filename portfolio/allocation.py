from typing import Dict, Tuple


def calculate_investment_allocation(
    target_allocation: Dict[str, float],
    investment_amount: float,
    current_portfolio: Dict[str, float],
) -> Tuple[str, float]:
    """
    Calculates recommended investments to move towards target allocation.

    Args:
        target_allocation: dict of {str: float} - target allocation percentages for each security
        investment_amount: float - amount of money to invest
        current_portfolio: dict of {str: float} - current portfolio values for each security

    Returns:
        tuple of (str, float) - highest priority security to invest in and recommended amount
    """
    if not target_allocation or investment_amount <= 0:
        return None, 0.0

    total_current_value = sum(current_portfolio.values()) if current_portfolio else 0.0
    total_future_value = total_current_value + investment_amount

    if total_future_value <= 0:
        return None, 0.0

    # Calculate current allocation percentages
    current_allocation = {}
    for security in target_allocation:
        current_value = current_portfolio.get(security, 0.0)
        current_allocation[security] = (
            current_value / total_current_value if total_current_value > 0 else 0.0
        )

    # Calculate the gap between target and current allocation for each security
    allocation_gaps = {}
    for security, target_percent in target_allocation.items():
        current_percent = current_allocation.get(security, 0.0)
        # Gap represents how much we're under-allocated (positive means need more)
        gap = target_percent - current_percent
        allocation_gaps[security] = gap

    # Find the security(ies) with the largest gap (most under-allocated)
    max_gap_securities = sorted(
        allocation_gaps.items(), key=lambda item: item[1], reverse=True
    )
    selected_security = max_gap_securities[0][0] if max_gap_securities else None

    # Calculate recommended investment amount for the selected security
    target_value = target_allocation[selected_security] * total_future_value
    current_value = current_portfolio.get(selected_security, 0.0)
    needed_investment = target_value - current_value

    # The recommended amount is the minimum of what's needed and what's available
    recommended_amount = min(investment_amount, max(0.0, needed_investment))

    return selected_security, recommended_amount
