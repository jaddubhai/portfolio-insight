import json
import logging
from logging.handlers import RotatingFileHandler

# logger settings
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler("python_client.log", maxBytes=5 * 1024 * 1024, backupCount=3)
FORMAT = "%(asctime)-15s %(message)s"
fmt = logging.Formatter(FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(fmt)
logger.addHandler(handler)


class Market:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def quotes(self, symbols):
        """
        Calls quotes API to provide quote details for equities, options, and mutual funds

        :param self: Passes authenticated session in parameter
        :param symbols: Stock symbol(s) to get quotes for
        :return: List of quote data or None if error
        """
        if not symbols:
            return None

        # URL for the API endpoint
        url = self.base_url + "/v1/market/quote/" + symbols + ".json"

        # Make API call for GET request
        response = self.session.get(url)
        logger.debug("Request Header: %s", response.request.headers)

        if response is not None and response.status_code == 200:

            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))

            # Handle and parse response
            data = response.json()
            if data is not None and "QuoteResponse" in data and "QuoteData" in data["QuoteResponse"]:
                quotes_list = []
                for quote in data["QuoteResponse"]["QuoteData"]:
                    quote_data = {}
                    if quote is not None and "dateTime" in quote:
                        quote_data["dateTime"] = quote["dateTime"]
                    if quote is not None and "Product" in quote and "symbol" in quote["Product"]:
                        quote_data["symbol"] = quote["Product"]["symbol"]
                    if quote is not None and "Product" in quote and "securityType" in quote["Product"]:
                        quote_data["securityType"] = quote["Product"]["securityType"]
                    if quote is not None and "All" in quote and "lastTrade" in quote["All"]:
                        quote_data["lastPrice"] = quote["All"]["lastTrade"]
                    if quote is not None and "All" in quote and "changeClose" in quote["All"]:
                        quote_data["changeClose"] = quote["All"]["changeClose"]
                    if quote is not None and "All" in quote and "changeClosePercentage" in quote["All"]:
                        quote_data["changeClosePercentage"] = quote["All"]["changeClosePercentage"]
                    if quote is not None and "All" in quote and "previousClose" in quote["All"]:
                        quote_data["previousClose"] = quote["All"]["previousClose"]
                    if quote is not None and "All" in quote and "bid" in quote["All"]:
                        quote_data["bid"] = quote["All"]["bid"]
                    if quote is not None and "All" in quote and "bidSize" in quote["All"]:
                        quote_data["bidSize"] = quote["All"]["bidSize"]
                    if quote is not None and "All" in quote and "ask" in quote["All"]:
                        quote_data["ask"] = quote["All"]["ask"]
                    if quote is not None and "All" in quote and "askSize" in quote["All"]:
                        quote_data["askSize"] = quote["All"]["askSize"]
                    if quote is not None and "All" in quote and "low" in quote["All"]:
                        quote_data["low"] = quote["All"]["low"]
                    if quote is not None and "All" in quote and "high" in quote["All"]:
                        quote_data["high"] = quote["All"]["high"]
                    if quote is not None and "All" in quote and "totalVolume" in quote["All"]:
                        quote_data["totalVolume"] = quote["All"]["totalVolume"]
                    quotes_list.append(quote_data)
                return quotes_list
            else:
                # Handle errors
                if data is not None and 'QuoteResponse' in data and 'Messages' in data["QuoteResponse"] \
                        and 'Message' in data["QuoteResponse"]["Messages"] \
                        and data["QuoteResponse"]["Messages"]["Message"] is not None:
                    error_messages = []
                    for error_message in data["QuoteResponse"]["Messages"]["Message"]:
                        error_messages.append(error_message["description"])
                    logger.debug("Quote API errors: %s", error_messages)
                    return None
                else:
                    logger.debug("Quote API service error")
                    return None
        else:
            logger.debug("Response Body: %s", response)
            return None
