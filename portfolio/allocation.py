from typing import Dict, Optional, List, Any
import math
import sys
import os

# Add parent directory to path for importing utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils


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

    total_current_value = (
        sum(current_allocation.values()) if current_allocation else 0.0
    )
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
    under_allocated = {
        t: allocation_gaps[t] for t in allocation_gaps if allocation_gaps[t] > 0
    }

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
            shares_to_buy[security] = math.floor(
                allocation_amount / current_prices[security]
            )
        else:
            shares_to_buy[security] = 0

    return shares_to_buy


class AllocationService:
    """
    End-to-end service for investment allocation that integrates session management,
    account selection, portfolio data, market data, and allocation calculation.
    """

    def __init__(self):
        """Initialize the allocation service."""
        self.session = None
        self.base_url = None
        self.accounts_client = None
        self.market_client = None
        self.current_account = None

    def start_session(
        self, key_type: utils.KeyType = utils.KeyType.SANDBOX
    ) -> Dict[str, Any]:
        """
        Start an authenticated session using OAuth.

        Args:
            key_type: KeyType enum for SANDBOX or LIVE environment

        Returns:
            Dictionary containing success status and session info
        """
        try:
            self.base_url, self.session = utils.oauth(key_type)
            self.accounts_client = utils.account_instance(self.base_url, self.session)
            self.market_client = utils.market_instance(self.base_url, self.session)
            return {
                "success": True,
                "message": "Session started successfully",
                "environment": key_type.value,
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to start session: {str(e)}"}

    def get_accounts(self) -> Dict[str, Any]:
        """
        Get list of available accounts for the authenticated user.

        Returns:
            Dictionary containing success status and accounts list
        """
        if not self.accounts_client:
            return {
                "success": False,
                "error": "Session not started. Please call start_session() first.",
            }

        try:
            result = self.accounts_client.account_list()
            return result
        except Exception as e:
            return {"success": False, "error": f"Failed to retrieve accounts: {str(e)}"}

    def set_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set the active account for portfolio operations.

        Args:
            account_data: Dictionary containing account information with required fields

        Returns:
            Dictionary containing success status
        """
        if not self.accounts_client:
            return {
                "success": False,
                "error": "Session not started. Please call start_session() first.",
            }

        try:
            result = self.accounts_client.set_account(account_data)
            if result["success"]:
                self.current_account = account_data
            return result
        except Exception as e:
            return {"success": False, "error": f"Failed to set account: {str(e)}"}

    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive account summary including balance and portfolio.

        Returns:
            Dictionary containing account summary or error information
        """
        if not self.accounts_client:
            return {
                "success": False,
                "error": "Session not started. Please call start_session() first.",
            }

        if not self.current_account:
            return {
                "success": False,
                "error": "No account selected. Please call set_account() first.",
            }

        try:
            return self.accounts_client.get_account_summary()
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get account summary: {str(e)}",
            }

    def get_current_portfolio_allocation(self) -> Dict[str, Any]:
        """
        Get current portfolio positions formatted for allocation calculation.

        Returns:
            Dictionary containing current allocation values keyed by symbol
        """
        if not self.accounts_client or not self.current_account:
            return {
                "success": False,
                "error": "Session not started or account not selected.",
            }

        try:
            portfolio_result = self.accounts_client.portfolio()
            if not portfolio_result["success"]:
                return portfolio_result

            # Convert portfolio positions to allocation format
            current_allocation = {}
            positions = portfolio_result["positions"]

            for position in positions:
                symbol = position.get("symbol")
                market_value = position.get("market_value", 0)

                if symbol and market_value:
                    current_allocation[symbol] = float(market_value)

            return {
                "success": True,
                "current_allocation": current_allocation,
                "positions": positions,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get portfolio allocation: {str(e)}",
            }

    def get_current_prices(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get current market prices for the specified symbols.

        Args:
            symbols: List of stock symbols to get prices for

        Returns:
            Dictionary containing current prices keyed by symbol
        """
        if not self.market_client:
            return {
                "success": False,
                "error": "Session not started. Please call start_session() first.",
            }

        try:
            quotes_result = self.market_client.get_multiple_quotes(symbols)
            if not quotes_result["success"]:
                return quotes_result

            # Convert quotes to prices format
            current_prices = {}
            quotes = quotes_result["quotes"]

            for quote in quotes:
                symbol = quote.get("symbol")
                last_price = quote.get("last_price")

                if symbol and last_price:
                    current_prices[symbol] = float(last_price)

            return {"success": True, "current_prices": current_prices, "quotes": quotes}

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get current prices: {str(e)}",
            }

    def calculate_allocation(
        self, target_allocation: Dict[str, float], investment_amount: float
    ) -> Dict[str, Any]:
        """
        Calculate investment allocation using current portfolio and market data.

        Args:
            target_allocation: Target allocation percentages for each security
            investment_amount: Amount of money to invest

        Returns:
            Dictionary containing allocation recommendations and supporting data
        """
        if (
            not self.accounts_client
            or not self.market_client
            or not self.current_account
        ):
            return {
                "success": False,
                "error": "Session not started or account not selected.",
            }

        try:
            # Get current portfolio allocation
            portfolio_result = self.get_current_portfolio_allocation()
            if not portfolio_result["success"]:
                return portfolio_result

            current_allocation = portfolio_result["current_allocation"]

            # Get current market prices for target securities
            symbols = list(target_allocation.keys())
            prices_result = self.get_current_prices(symbols)
            if not prices_result["success"]:
                return prices_result

            current_prices = prices_result["current_prices"]

            # Validate that we have prices for all target securities
            missing_prices = [
                symbol for symbol in symbols if symbol not in current_prices
            ]
            if missing_prices:
                return {
                    "success": False,
                    "error": f"Missing current prices for: {', '.join(missing_prices)}",
                }

            # Calculate investment allocation
            allocation_result = calculate_investment_allocation(
                target_allocation=target_allocation,
                investment_amount=investment_amount,
                current_allocation=current_allocation,
                current_prices=current_prices,
            )

            # Calculate investment summary
            total_investment_value = sum(
                allocation_result.get(symbol, 0) * current_prices[symbol]
                for symbol in allocation_result
            )

            allocation_breakdown = {}
            for symbol, shares in allocation_result.items():
                investment_value = shares * current_prices[symbol]
                allocation_breakdown[symbol] = {
                    "shares": shares,
                    "price_per_share": current_prices[symbol],
                    "investment_value": investment_value,
                    "percentage_of_investment": (
                        (investment_value / investment_amount * 100)
                        if investment_amount > 0
                        else 0
                    ),
                }

            return {
                "success": True,
                "allocation_recommendations": allocation_result,
                "allocation_breakdown": allocation_breakdown,
                "total_investment_value": total_investment_value,
                "unused_cash": investment_amount - total_investment_value,
                "target_allocation": target_allocation,
                "current_allocation": current_allocation,
                "current_prices": current_prices,
                "investment_amount": investment_amount,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to calculate allocation: {str(e)}",
            }

    def get_allocation_summary(
        self, target_allocation: Dict[str, float], investment_amount: float
    ) -> Dict[str, Any]:
        """
        Get a comprehensive allocation summary including account info and recommendations.

        Args:
            target_allocation: Target allocation percentages for each security
            investment_amount: Amount of money to invest

        Returns:
            Dictionary containing complete allocation analysis
        """
        try:
            # Get account summary
            account_summary = self.get_account_summary()
            if not account_summary["success"]:
                return account_summary

            # Get allocation calculation
            allocation_result = self.calculate_allocation(
                target_allocation, investment_amount
            )
            if not allocation_result["success"]:
                return allocation_result

            return {
                "success": True,
                "account_summary": account_summary["account_summary"],
                "allocation_analysis": allocation_result,
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get allocation summary: {str(e)}",
            }

    def is_session_active(self) -> bool:
        """Check if there's an active session."""
        return self.session is not None and self.accounts_client is not None

    def is_account_selected(self) -> bool:
        """Check if an account has been selected."""
        return self.current_account is not None

    def get_session_status(self) -> Dict[str, Any]:
        """Get current session and account status."""
        return {
            "session_active": self.is_session_active(),
            "account_selected": self.is_account_selected(),
            "current_account": self.current_account,
            "base_url": self.base_url,
        }
