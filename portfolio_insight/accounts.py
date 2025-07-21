import json
import logging
import configparser
from . import utils
from logging.handlers import RotatingFileHandler

# loading configuration file
config = configparser.ConfigParser()
config.read("config.ini")

# logger settings
logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    "python_client.log", maxBytes=5 * 1024 * 1024, backupCount=3
)
FORMAT = "%(asctime)-15s %(message)s"
fmt = logging.Formatter(FORMAT, datefmt="%m/%d/%Y %I:%M:%S %p")
handler.setFormatter(fmt)
logger.addHandler(handler)


class Accounts:
    def __init__(self, session, base_url):
        """
        Initialize Accounts object with session and account information

        :param session: authenticated session
        """
        self.session = session
        self.account = {}
        self.base_url = base_url

    def account_list(self):
        """
        Calls account list API to retrieve a list of the user's E*TRADE accounts

        :return: Dictionary containing success status and accounts data or error information
        """

        url = self.base_url + "/v1/accounts/list.json"
        response = self.session.get(url, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )

            data = response.json()
            if (
                data is not None
                and "AccountListResponse" in data
                and "Accounts" in data["AccountListResponse"]
                and "Account" in data["AccountListResponse"]["Accounts"]
            ):
                accounts = data["AccountListResponse"]["Accounts"]["Account"]
                return {"success": True, "accounts": accounts}
            else:
                logger.debug("Response Body: %s", response.text)
                if (
                    response is not None
                    and response.headers["Content-Type"] == "application/json"
                    and "Error" in response.json()
                    and "message" in response.json()["Error"]
                    and response.json()["Error"]["message"] is not None
                ):
                    return {"success": False, "error": data["Error"]["message"]}
                else:
                    return {"success": False, "error": "AccountList API service error"}
        else:
            logger.debug("Response Body: %s", response.text)
            if (
                response is not None
                and response.headers["Content-Type"] == "application/json"
                and "Error" in response.json()
                and "message" in response.json()["Error"]
                and response.json()["Error"]["message"] is not None
            ):
                return {"success": False, "error": response.json()["Error"]["message"]}
            else:
                return {"success": False, "error": "AccountList API service error"}

    def portfolio(self):
        """
        Call portfolio API to retrieve a list of positions held in the specified account

        :return: Dictionary containing success status and portfolio positions or error information
        """
        if not self.account or "accountIdKey" not in self.account:
            return {
                "success": False,
                "error": "Account not selected. Please set account first.",
            }

        url = (
            self.base_url
            + "/v1/accounts/"
            + self.account["accountIdKey"]
            + "/portfolio.json"
        )
        response = self.session.get(url, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )
            data = response.json()

            if (
                data is not None
                and "PortfolioResponse" in data
                and "AccountPortfolio" in data["PortfolioResponse"]
            ):
                positions_list = []
                for acctPortfolio in data["PortfolioResponse"]["AccountPortfolio"]:
                    if acctPortfolio is not None and "Position" in acctPortfolio:
                        for position in acctPortfolio["Position"]:
                            cleaned_position = {}
                            if position is not None and "symbolDescription" in position:
                                cleaned_position["symbol"] = position[
                                    "symbolDescription"
                                ]
                            if position is not None and "quantity" in position:
                                cleaned_position["quantity"] = position["quantity"]
                            if (
                                position is not None
                                and "Quick" in position
                                and "lastTrade" in position["Quick"]
                            ):
                                cleaned_position["last_price"] = position["Quick"][
                                    "lastTrade"
                                ]
                            if position is not None and "pricePaid" in position:
                                cleaned_position["price_paid"] = position["pricePaid"]
                            if position is not None and "totalGain" in position:
                                cleaned_position["total_gain"] = position["totalGain"]
                            if position is not None and "marketValue" in position:
                                cleaned_position["market_value"] = position[
                                    "marketValue"
                                ]
                            # Add additional position details if available
                            if position is not None and "Product" in position:
                                product = position["Product"]
                                if "securityType" in product:
                                    cleaned_position["security_type"] = product[
                                        "securityType"
                                    ]
                                if "symbol" in product:
                                    cleaned_position["product_symbol"] = product[
                                        "symbol"
                                    ]

                            positions_list.append(cleaned_position)
                return {"success": True, "positions": positions_list}
            else:
                logger.debug("Response Body: %s", response.text)
                if (
                    response is not None
                    and "headers" in response
                    and "Content-Type" in response.headers
                    and response.headers["Content-Type"] == "application/json"
                    and "Error" in response.json()
                    and "message" in response.json()["Error"]
                    and response.json()["Error"]["message"] is not None
                ):
                    return {
                        "success": False,
                        "error": response.json()["Error"]["message"],
                    }
                else:
                    return {"success": False, "error": "Portfolio API service error"}
        else:
            logger.debug("Response Body: %s", response.text)
            if (
                response is not None
                and "headers" in response
                and "Content-Type" in response.headers
                and response.headers["Content-Type"] == "application/json"
                and "Error" in response.json()
                and "message" in response.json()["Error"]
                and response.json()["Error"]["message"] is not None
            ):
                return {"success": False, "error": response.json()["Error"]["message"]}
            else:
                return {"success": False, "error": "Portfolio API service error"}

    def balance(self):
        """
        Calls account balance API to retrieve the current balance and related details for a specified account

        :return: Dictionary containing success status and balance information or error information
        """
        if not self.account or "accountIdKey" not in self.account:
            return {
                "success": False,
                "error": "Account not selected. Please set account first.",
            }

        url = (
            self.base_url
            + "/v1/accounts/"
            + self.account["accountIdKey"]
            + "/balance.json"
        )
        params = {"instType": self.account["institutionType"], "realTimeNAV": "true"}
        headers = {"consumerkey": config["DEFAULT"]["CONSUMER_KEY"]}

        response = self.session.get(
            url, header_auth=True, params=params, headers=headers
        )
        logger.debug("Request url: %s", url)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )
            data = response.json()
            if data is not None and "BalanceResponse" in data:
                balance_data = data["BalanceResponse"]
                result = {}
                if balance_data is not None and "accountId" in balance_data:
                    result["accountId"] = balance_data["accountId"]
                if balance_data is not None and "accountDescription" in balance_data:
                    result["accountDescription"] = balance_data["accountDescription"]
                if balance_data is not None and "Computed" in balance_data:
                    computed = balance_data["Computed"]
                    if (
                        "RealTimeValues" in computed
                        and "totalAccountValue" in computed["RealTimeValues"]
                    ):
                        result["netAccountValue"] = computed["RealTimeValues"][
                            "totalAccountValue"
                        ]
                    if "marginBuyingPower" in computed:
                        result["marginBuyingPower"] = computed["marginBuyingPower"]
                    if "cashBuyingPower" in computed:
                        result["cashBuyingPower"] = computed["cashBuyingPower"]
                return {"success": True, "balance": result}
            else:
                logger.debug("Response Body: %s", response.text)
                if (
                    response is not None
                    and response.headers["Content-Type"] == "application/json"
                    and "Error" in response.json()
                    and "message" in response.json()["Error"]
                    and response.json()["Error"]["message"] is not None
                ):
                    return {
                        "success": False,
                        "error": response.json()["Error"]["message"],
                    }
                else:
                    return {"success": False, "error": "Balance API service error"}
        else:
            logger.debug("Response Body: %s", response.text)
            if (
                response is not None
                and response.headers["Content-Type"] == "application/json"
                and "Error" in response.json()
                and "message" in response.json()["Error"]
                and response.json()["Error"]["message"] is not None
            ):
                return {"success": False, "error": response.json()["Error"]["message"]}
            else:
                return {"success": False, "error": "Balance API service error"}

    def set_account(self, account_data):
        """
        Set the current account for portfolio and balance operations

        :param account_data: Dictionary containing account information
        :return: Dictionary containing success status
        """
        if not account_data:
            return {"success": False, "error": "Account data is required"}

        required_fields = ["accountIdKey", "institutionType"]
        for field in required_fields:
            if field not in account_data:
                return {"success": False, "error": f"Missing required field: {field}"}

        self.account = account_data
        return {"success": True, "message": "Account set successfully"}

    def get_account_summary(self):
        """
        Get a comprehensive summary of the current account including balance and portfolio

        :return: Dictionary containing account summary or error information
        """
        if not self.account:
            return {
                "success": False,
                "error": "Account not selected. Please set account first.",
            }

        # Get balance information
        balance_result = self.balance()
        if not balance_result["success"]:
            return balance_result

        # Get portfolio information
        portfolio_result = self.portfolio()
        if not portfolio_result["success"]:
            return portfolio_result

        # Calculate portfolio summary statistics
        positions = portfolio_result["positions"]
        portfolio_summary = {
            "total_positions": len(positions),
            "total_market_value": sum(pos.get("market_value", 0) for pos in positions),
            "total_gain_loss": sum(pos.get("total_gain", 0) for pos in positions),
            "positions_with_gains": len(
                [pos for pos in positions if pos.get("total_gain", 0) > 0]
            ),
            "positions_with_losses": len(
                [pos for pos in positions if pos.get("total_gain", 0) < 0]
            ),
        }

        return {
            "success": True,
            "account_summary": {
                "account_info": {
                    "account_id": balance_result["balance"].get("accountId"),
                    "account_description": balance_result["balance"].get(
                        "accountDescription"
                    ),
                },
                "balance": balance_result["balance"],
                "portfolio_summary": portfolio_summary,
                "positions": positions,
            },
        }

    def get_account_info(self):
        """
        Get basic information about the currently selected account

        :return: Dictionary containing account information or error
        """
        if not self.account:
            return {"success": False, "error": "No account selected"}

        return {"success": True, "account": self.account}


if __name__ == "__main__":
    base_url, session = utils.oauth(utils.KeyType.LIVE)
    accounts_instance = utils.account_instance(base_url, session)

    try:
        current_accounts = accounts_instance.account_list()
        print("Current Accounts:", current_accounts)
    except Exception as e:
        print("Error fetching accounts:", e)
