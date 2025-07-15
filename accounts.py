import json
import logging
import configparser
import utils
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

        :param self:Passes in parameter authenticated session
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
                return accounts
            else:
                logger.debug("Response Body: %s", response.text)
                if (
                    response is not None
                    and response.headers["Content-Type"] == "application/json"
                    and "Error" in response.json()
                    and "message" in response.json()["Error"]
                    and response.json()["Error"]["message"] is not None
                ):
                    print("Error: " + data["Error"]["message"])
                else:
                    print("Error: AccountList API service error")
        else:
            logger.debug("Response Body: %s", response.text)
            if (
                response is not None
                and response.headers["Content-Type"] == "application/json"
                and "Error" in response.json()
                and "message" in response.json()["Error"]
                and response.json()["Error"]["message"] is not None
            ):
                print("Error: " + response.json()["Error"]["message"])
            else:
                print("Error: AccountList API service error")

    def portfolio(self):
        """
        Call portfolio API to retrieve a list of positions held in the specified account

        :param self: Passes in parameter authenticated session and information on selected account
        """
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
                            positions_list.append(cleaned_position)
                return positions_list
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
                    print("Error: " + response.json()["Error"]["message"])
                else:
                    print("Error: Portfolio API service error")
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
                print("Error: " + response.json()["Error"]["message"])
            else:
                print("Error: Portfolio API service error")

    def balance(self):
        """
        Calls account balance API to retrieve the current balance and related details for a specified account

        :param self: Pass in parameters authenticated session and information on selected account
        """

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
                return result
            else:
                logger.debug("Response Body: %s", response.text)
                if (
                    response is not None
                    and response.headers["Content-Type"] == "application/json"
                    and "Error" in response.json()
                    and "message" in response.json()["Error"]
                    and response.json()["Error"]["message"] is not None
                ):
                    print("Error: " + response.json()["Error"]["message"])
                else:
                    print("Error: Balance API service error")
        else:
            logger.debug("Response Body: %s", response.text)
            if (
                response is not None
                and response.headers["Content-Type"] == "application/json"
                and "Error" in response.json()
                and "message" in response.json()["Error"]
                and response.json()["Error"]["message"] is not None
            ):
                print("Error: " + response.json()["Error"]["message"])
            else:
                print("Error: Balance API service error")


if __name__ == "__main__":
    base_url, session = utils.oauth(utils.KeyType.LIVE)
    accounts_instance = utils.account_instance(base_url, session)

    try:
        current_accounts = accounts_instance.account_list()
        print("Current Accounts:", current_accounts)
    except Exception as e:
        print("Error fetching accounts:", e)
