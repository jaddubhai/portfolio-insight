import json
import logging
from logging.handlers import RotatingFileHandler

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


class Market:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def get_quote(self, symbol):
        """
        Calls quotes API to provide quote details for equities, options, and mutual funds

        :param symbol: Stock symbol to get quote for
        :return: Dictionary containing quote data or error information
        """
        if not symbol:
            return {"success": False, "error": "Symbol is required"}

        # URL for the API endpoint
        url = self.base_url + "/v1/market/quote/" + symbol + ".json"

        # Make API call for GET request
        response = self.session.get(url)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )

            # Handle and parse response
            data = response.json()
            if (
                data is not None
                and "QuoteResponse" in data
                and "QuoteData" in data["QuoteResponse"]
            ):
                quotes_list = []
                for quote in data["QuoteResponse"]["QuoteData"]:
                    quote_data = {}

                    if quote is not None and "dateTime" in quote:
                        quote_data["date_time"] = quote["dateTime"]

                    if (
                        quote is not None
                        and "Product" in quote
                        and "symbol" in quote["Product"]
                    ):
                        quote_data["symbol"] = quote["Product"]["symbol"]

                    if (
                        quote is not None
                        and "Product" in quote
                        and "securityType" in quote["Product"]
                    ):
                        quote_data["security_type"] = quote["Product"]["securityType"]

                    if (
                        quote is not None
                        and "All" in quote
                        and "lastTrade" in quote["All"]
                    ):
                        quote_data["last_price"] = quote["All"]["lastTrade"]
                        quote_data["open"] = quote["All"]["lastTrade"]

                    if (
                        quote is not None
                        and "All" in quote
                        and "changeClose" in quote["All"]
                        and "changeClosePercentage" in quote["All"]
                    ):
                        quote_data["change"] = quote["All"]["changeClose"]
                        quote_data["change_percentage"] = quote["All"][
                            "changeClosePercentage"
                        ]

                    if (
                        quote is not None
                        and "All" in quote
                        and "previousClose" in quote["All"]
                    ):
                        quote_data["previous_close"] = quote["All"]["previousClose"]

                    if (
                        quote is not None
                        and "All" in quote
                        and "bid" in quote["All"]
                        and "bidSize" in quote["All"]
                    ):
                        quote_data["bid"] = quote["All"]["bid"]
                        quote_data["bid_size"] = quote["All"]["bidSize"]

                    if (
                        quote is not None
                        and "All" in quote
                        and "ask" in quote["All"]
                        and "askSize" in quote["All"]
                    ):
                        quote_data["ask"] = quote["All"]["ask"]
                        quote_data["ask_size"] = quote["All"]["askSize"]

                    if (
                        quote is not None
                        and "All" in quote
                        and "low" in quote["All"]
                        and "high" in quote["All"]
                    ):
                        quote_data["day_low"] = quote["All"]["low"]
                        quote_data["day_high"] = quote["All"]["high"]

                    if (
                        quote is not None
                        and "All" in quote
                        and "totalVolume" in quote["All"]
                    ):
                        quote_data["volume"] = quote["All"]["totalVolume"]

                    quotes_list.append(quote_data)

                return {"success": True, "quotes": quotes_list}
            else:
                # Handle errors
                error_messages = []
                if (
                    data is not None
                    and "QuoteResponse" in data
                    and "Messages" in data["QuoteResponse"]
                    and "Message" in data["QuoteResponse"]["Messages"]
                    and data["QuoteResponse"]["Messages"]["Message"] is not None
                ):
                    for error_message in data["QuoteResponse"]["Messages"]["Message"]:
                        error_messages.append(error_message["description"])
                    return {"success": False, "error": "; ".join(error_messages)}
                else:
                    return {"success": False, "error": "Quote API service error"}
        else:
            logger.debug("Response Body: %s", response)
            return {"success": False, "error": "Quote API service error"}

    def get_multiple_quotes(self, symbols):
        """
        Get quotes for multiple symbols

        :param symbols: List of stock symbols or comma-separated string
        :return: Dictionary containing quotes data for all symbols
        """
        if not symbols:
            return {"success": False, "error": "Symbols are required"}

        # Handle both list and string inputs
        if isinstance(symbols, list):
            symbols_str = ",".join(symbols)
        else:
            symbols_str = symbols

        return self.get_quote(symbols_str)
