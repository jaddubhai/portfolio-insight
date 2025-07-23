#!/usr/bin/env python3
"""
Test suite for the AllocationService class.
"""

from unittest.mock import Mock, patch, MagicMock

from portfolio_insight.portfolio.allocation import (
    AllocationService,
    calculate_investment_allocation,
)
from portfolio_insight import utils


class TestAllocationService:
    """Test class for AllocationService functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = AllocationService()

        # Mock session and clients
        self.mock_session = Mock()
        self.mock_base_url = "https://api.etrade.com/sandbox"
        self.mock_accounts_client = Mock()
        self.mock_market_client = Mock()

    def test_initialization(self):
        """Test AllocationService initialization."""
        service = AllocationService()
        assert service.session is None
        assert service.base_url is None
        assert service.accounts_client is None
        assert service.market_client is None
        assert service.current_account is None
        print("✓ Initialization test passed")

    @patch("portfolio_insight.utils.oauth")
    @patch("portfolio_insight.utils.account_instance")
    @patch("portfolio_insight.utils.market_instance")
    def test_start_session_success(
        self, mock_market_instance, mock_account_instance, mock_oauth
    ):
        """Test successful session start."""
        # Setup mocks
        mock_oauth.return_value = (self.mock_base_url, self.mock_session)
        mock_account_instance.return_value = self.mock_accounts_client
        mock_market_instance.return_value = self.mock_market_client

        # Test session start
        result = self.service.start_session(utils.KeyType.SANDBOX)

        # Assertions
        assert result["success"] is True
        assert result["environment"] == "sandbox"
        assert self.service.session == self.mock_session
        assert self.service.base_url == self.mock_base_url
        assert self.service.accounts_client == self.mock_accounts_client
        assert self.service.market_client == self.mock_market_client

        # Verify mock calls
        mock_oauth.assert_called_once_with(utils.KeyType.SANDBOX)
        mock_account_instance.assert_called_once_with(
            self.mock_base_url, self.mock_session
        )
        mock_market_instance.assert_called_once_with(
            self.mock_base_url, self.mock_session
        )
        print("✓ Start session success test passed")

    @patch("portfolio_insight.utils.oauth")
    def test_start_session_failure(self, mock_oauth):
        """Test session start failure."""
        # Setup mock to raise exception
        mock_oauth.side_effect = Exception("OAuth failed")

        # Test session start
        result = self.service.start_session()

        # Assertions
        assert result["success"] is False
        assert "OAuth failed" in result["error"]
        assert self.service.session is None
        print("✓ Start session failure test passed")

    def test_get_accounts_no_session(self):
        """Test get_accounts without active session."""
        result = self.service.get_accounts()

        assert result["success"] is False
        assert "Session not started" in result["error"]
        print("✓ Get accounts no session test passed")

    def test_get_accounts_success(self):
        """Test successful get_accounts."""
        # Setup service with mock client
        self.service.accounts_client = self.mock_accounts_client
        mock_accounts = [
            {"accountIdKey": "123", "institutionType": "BROKERAGE"},
            {"accountIdKey": "456", "institutionType": "BROKERAGE"},
        ]
        self.mock_accounts_client.account_list.return_value = {
            "success": True,
            "accounts": mock_accounts,
        }

        # Test get accounts
        result = self.service.get_accounts()

        # Assertions
        assert result["success"] is True
        assert result["accounts"] == mock_accounts
        self.mock_accounts_client.account_list.assert_called_once()
        print("✓ Get accounts success test passed")

    def test_set_account_no_session(self):
        """Test set_account without active session."""
        account_data = {"accountIdKey": "123", "institutionType": "BROKERAGE"}
        result = self.service.set_account(account_data)

        assert result["success"] is False
        assert "Session not started" in result["error"]
        print("✓ Set account no session test passed")

    def test_set_account_success(self):
        """Test successful set_account."""
        # Setup service with mock client
        self.service.accounts_client = self.mock_accounts_client
        account_data = {"accountIdKey": "123", "institutionType": "BROKERAGE"}
        self.mock_accounts_client.set_account.return_value = {
            "success": True,
            "message": "Account set successfully",
        }

        # Test set account
        result = self.service.set_account(account_data)

        # Assertions
        assert result["success"] is True
        assert self.service.current_account == account_data
        self.mock_accounts_client.set_account.assert_called_once_with(account_data)
        print("✓ Set account success test passed")

    def test_get_current_portfolio_allocation_success(self):
        """Test successful portfolio allocation retrieval."""
        # Setup service
        self.service.accounts_client = self.mock_accounts_client
        self.service.current_account = {"accountIdKey": "123"}

        mock_positions = [
            {"symbol": "AAPL", "market_value": 1000.0},
            {"symbol": "GOOGL", "market_value": 500.0},
        ]
        self.mock_accounts_client.portfolio.return_value = {
            "success": True,
            "positions": mock_positions,
        }

        # Test get portfolio allocation
        result = self.service.get_current_portfolio_allocation()

        # Assertions
        assert result["success"] is True
        assert result["current_allocation"] == {"AAPL": 1000.0, "GOOGL": 500.0}
        assert result["positions"] == mock_positions
        print("✓ Get portfolio allocation success test passed")

    def test_get_current_prices_success(self):
        """Test successful current prices retrieval."""
        # Setup service
        self.service.market_client = self.mock_market_client

        mock_quotes = [
            {"symbol": "AAPL", "last_price": 150.0},
            {"symbol": "GOOGL", "last_price": 200.0},
        ]
        self.mock_market_client.get_multiple_quotes.return_value = {
            "success": True,
            "quotes": mock_quotes,
        }

        # Test get current prices
        symbols = ["AAPL", "GOOGL"]
        result = self.service.get_current_prices(symbols)

        # Assertions
        assert result["success"] is True
        assert result["current_prices"] == {"AAPL": 150.0, "GOOGL": 200.0}
        assert result["quotes"] == mock_quotes
        self.mock_market_client.get_multiple_quotes.assert_called_once_with(symbols)
        print("✓ Get current prices success test passed")

    def test_calculate_allocation_integration(self):
        """Test complete allocation calculation integration."""
        # Setup service with all mocks
        self.service.accounts_client = self.mock_accounts_client
        self.service.market_client = self.mock_market_client
        self.service.current_account = {"accountIdKey": "123"}

        # Mock portfolio response
        mock_positions = [
            {"symbol": "AAPL", "market_value": 600.0},
            {"symbol": "GOOGL", "market_value": 400.0},
        ]
        self.mock_accounts_client.portfolio.return_value = {
            "success": True,
            "positions": mock_positions,
        }

        # Mock market response
        mock_quotes = [
            {"symbol": "AAPL", "last_price": 150.0},
            {"symbol": "GOOGL", "last_price": 200.0},
        ]
        self.mock_market_client.get_multiple_quotes.return_value = {
            "success": True,
            "quotes": mock_quotes,
        }

        # Test data
        target_allocation = {"AAPL": 0.7, "GOOGL": 0.3}
        investment_amount = 1000.0

        # Test calculate allocation
        result = self.service.calculate_allocation(target_allocation, investment_amount)

        # Assertions
        assert result["success"] is True
        assert "allocation_recommendations" in result
        assert "allocation_breakdown" in result
        assert "total_investment_value" in result
        assert "unused_cash" in result
        assert result["target_allocation"] == target_allocation
        assert result["current_allocation"] == {"AAPL": 600.0, "GOOGL": 400.0}
        assert result["current_prices"] == {"AAPL": 150.0, "GOOGL": 200.0}
        assert result["investment_amount"] == investment_amount

        # Verify allocation calculation logic
        allocation_recommendations = result["allocation_recommendations"]
        for symbol, shares in allocation_recommendations.items():
            assert isinstance(shares, int)
            assert shares >= 0

        print("✓ Calculate allocation integration test passed")

    def test_session_status_methods(self):
        """Test session status checking methods."""
        # Test initial state
        assert not self.service.is_session_active()
        assert not self.service.is_account_selected()

        status = self.service.get_session_status()
        assert not status["session_active"]
        assert not status["account_selected"]
        assert status["current_account"] is None
        assert status["base_url"] is None

        # Test with session active
        self.service.session = self.mock_session
        self.service.accounts_client = self.mock_accounts_client
        self.service.base_url = self.mock_base_url

        assert self.service.is_session_active()
        assert not self.service.is_account_selected()

        # Test with account selected
        self.service.current_account = {"accountIdKey": "123"}

        assert self.service.is_session_active()
        assert self.service.is_account_selected()

        status = self.service.get_session_status()
        assert status["session_active"]
        assert status["account_selected"]
        assert status["current_account"] == {"accountIdKey": "123"}
        assert status["base_url"] == self.mock_base_url

        print("✓ Session status methods test passed")

    def test_missing_prices_handling(self):
        """Test handling of missing market prices."""
        # Setup service
        self.service.accounts_client = self.mock_accounts_client
        self.service.market_client = self.mock_market_client
        self.service.current_account = {"accountIdKey": "123"}

        # Mock portfolio response
        self.mock_accounts_client.portfolio.return_value = {
            "success": True,
            "positions": [{"symbol": "AAPL", "market_value": 1000.0}],
        }

        # Mock market response with missing price
        self.mock_market_client.get_multiple_quotes.return_value = {
            "success": True,
            "quotes": [],  # No quotes returned
        }

        # Test data
        target_allocation = {"AAPL": 0.6, "GOOGL": 0.4}
        investment_amount = 1000.0

        # Test calculate allocation
        result = self.service.calculate_allocation(target_allocation, investment_amount)

        # Assertions
        assert result["success"] is False
        assert "Missing current prices" in result["error"]
        print("✓ Missing prices handling test passed")


def run_allocation_service_tests():
    """Run all AllocationService tests."""
    print("Running AllocationService tests...")
    print("=" * 60)

    test_class = TestAllocationService()

    # Run all test methods
    test_methods = [method for method in dir(test_class) if method.startswith("test_")]

    for test_method in test_methods:
        test_class.setup_method()
        getattr(test_class, test_method)()

    print("=" * 60)
    print("✓ All AllocationService tests passed!")


def test_end_to_end_flow_simulation():
    """Test the complete end-to-end flow with mocked data."""
    print("\nTesting complete end-to-end flow simulation...")

    # This would simulate a UI workflow:
    # 1. Start session
    # 2. Get accounts
    # 3. Select account
    # 4. Calculate allocation

    service = AllocationService()

    # Mock the entire flow without actual API calls
    with patch("portfolio_insight.utils.oauth") as mock_oauth, patch(
        "portfolio_insight.utils.account_instance"
    ) as mock_account_instance, patch(
        "portfolio_insight.utils.market_instance"
    ) as mock_market_instance:

        # Setup mocks
        mock_session = Mock()
        mock_base_url = "https://api.etrade.com/sandbox"
        mock_accounts_client = Mock()
        mock_market_client = Mock()

        mock_oauth.return_value = (mock_base_url, mock_session)
        mock_account_instance.return_value = mock_accounts_client
        mock_market_instance.return_value = mock_market_client

        # Mock responses
        mock_accounts_client.account_list.return_value = {
            "success": True,
            "accounts": [{"accountIdKey": "123", "institutionType": "BROKERAGE"}],
        }

        mock_accounts_client.set_account.return_value = {
            "success": True,
            "message": "Account set successfully",
        }

        mock_accounts_client.portfolio.return_value = {
            "success": True,
            "positions": [
                {"symbol": "AAPL", "market_value": 5000.0},
                {"symbol": "GOOGL", "market_value": 3000.0},
            ],
        }

        mock_market_client.get_multiple_quotes.return_value = {
            "success": True,
            "quotes": [
                {"symbol": "AAPL", "last_price": 150.0},
                {"symbol": "GOOGL", "last_price": 200.0},
                {"symbol": "MSFT", "last_price": 100.0},
            ],
        }

        # Step 1: Start session
        session_result = service.start_session(utils.KeyType.SANDBOX)
        assert session_result["success"], f"Session start failed: {session_result}"

        # Step 2: Get accounts
        accounts_result = service.get_accounts()
        assert accounts_result["success"], f"Get accounts failed: {accounts_result}"

        # Step 3: Select account
        account_data = accounts_result["accounts"][0]
        set_account_result = service.set_account(account_data)
        assert set_account_result[
            "success"
        ], f"Set account failed: {set_account_result}"

        # Step 4: Calculate allocation
        target_allocation = {"AAPL": 0.5, "GOOGL": 0.3, "MSFT": 0.2}
        investment_amount = 2000.0

        allocation_result = service.calculate_allocation(
            target_allocation, investment_amount
        )
        assert allocation_result[
            "success"
        ], f"Allocation calculation failed: {allocation_result}"

        # Verify the results
        assert "allocation_recommendations" in allocation_result
        assert "allocation_breakdown" in allocation_result
        assert allocation_result["investment_amount"] == investment_amount
        assert allocation_result["target_allocation"] == target_allocation

        print("✓ End-to-end flow simulation test passed")

        # Print sample output for verification
        print("\nSample allocation result:")
        recommendations = allocation_result["allocation_recommendations"]
        breakdown = allocation_result["allocation_breakdown"]

        for symbol in recommendations:
            shares = recommendations[symbol]
            if shares > 0:
                details = breakdown[symbol]
                print(
                    f"  {symbol}: {shares} shares @ ${details['price_per_share']:.2f} = ${details['investment_value']:.2f}"
                )

        print(
            f"Total investment value: ${allocation_result['total_investment_value']:.2f}"
        )
        print(f"Unused cash: ${allocation_result['unused_cash']:.2f}")


if __name__ == "__main__":
    # Run allocation service tests
    run_allocation_service_tests()

    # Run end-to-end simulation
    test_end_to_end_flow_simulation()

    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
