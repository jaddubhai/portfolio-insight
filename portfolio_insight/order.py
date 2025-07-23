import json
import logging
from logging.handlers import RotatingFileHandler
import configparser
import random
import re

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


class Order:
    def __init__(self, session, account, base_url):
        self.session = session
        self.account = account
        self.base_url = base_url

    def _validate_order_params(self, order_params):
        """
        Validate order parameters

        :param order_params: Dictionary containing order parameters
        :return: Boolean indicating if parameters are valid
        """
        required_fields = ["symbol", "order_action", "quantity", "price_type"]

        for field in required_fields:
            if field not in order_params or not order_params[field]:
                return False

        # Validate price_type and related fields
        if order_params["price_type"] not in ["MARKET", "LIMIT"]:
            return False

        if order_params["price_type"] == "LIMIT" and (
            "limit_price" not in order_params or not order_params["limit_price"]
        ):
            return False

        # Validate order_action
        if order_params["order_action"] not in [
            "BUY",
            "SELL",
            "BUY_TO_COVER",
            "SELL_SHORT",
        ]:
            return False

        # Validate quantity is numeric
        try:
            int(order_params["quantity"])
        except (ValueError, TypeError):
            return False

        return True

    def preview_order(self, order_params):
        """
        Call preview order API based on provided order parameters

        :param self: Pass in authenticated session and information on selected account
        :param order_params: Dictionary containing order parameters
        :return: Dictionary containing preview response or error information
        """

        # Validate order parameters
        if not self._validate_order_params(order_params):
            return {"success": False, "error": "Invalid order parameters"}

        # Generate client order ID if not provided
        order = order_params.copy()
        if "client_order_id" not in order or not order["client_order_id"]:
            order["client_order_id"] = random.randint(1000000000, 9999999999)

        # URL for the API endpoint
        url = (
            self.base_url
            + "/v1/accounts/"
            + self.account["accountIdKey"]
            + "/orders/preview.json"
        )

        # Add parameters and header information
        headers = {
            "Content-Type": "application/xml",
            "consumerKey": config["DEFAULT"]["CONSUMER_KEY"],
        }

        # Add payload for POST Request
        payload = """<PreviewOrderRequest>
                       <orderType>EQ</orderType>
                       <clientOrderId>{0}</clientOrderId>
                       <Order>
                           <allOrNone>false</allOrNone>
                           <priceType>{1}</priceType>
                           <orderTerm>{2}</orderTerm>
                           <marketSession>REGULAR</marketSession>
                           <stopPrice></stopPrice>
                           <limitPrice>{3}</limitPrice>
                           <Instrument>
                               <Product>
                                   <securityType>EQ</securityType>
                                   <symbol>{4}</symbol>
                               </Product>
                               <orderAction>{5}</orderAction>
                               <quantityType>QUANTITY</quantityType>
                               <quantity>{6}</quantity>
                           </Instrument>
                       </Order>
                   </PreviewOrderRequest>"""
        payload = payload.format(
            order["client_order_id"],
            order["price_type"],
            order.get("order_term", "GOOD_FOR_DAY"),
            order.get("limit_price", ""),
            order["symbol"],
            order["order_action"],
            order["quantity"],
        )

        # Make API call for POST request
        response = self.session.post(
            url, header_auth=True, headers=headers, data=payload
        )
        logger.debug("Request Header: %s", response.request.headers)
        logger.debug("Request payload: %s", payload)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )
            data = response.json()

            result = {"success": True, "preview_data": {}}

            if (
                data is not None
                and "PreviewOrderResponse" in data
                and "PreviewIds" in data["PreviewOrderResponse"]
            ):
                result["preview_data"]["preview_ids"] = []
                for previewids in data["PreviewOrderResponse"]["PreviewIds"]:
                    result["preview_data"]["preview_ids"].append(
                        {"preview_id": previewids.get("previewId")}
                    )

            if (
                data is not None
                and "PreviewOrderResponse" in data
                and "Order" in data["PreviewOrderResponse"]
            ):
                result["preview_data"]["orders"] = []
                for orders in data["PreviewOrderResponse"]["Order"]:
                    order_info = {
                        "limit_price": orders.get("limitPrice"),
                        "price_type": orders.get("priceType"),
                        "order_term": orders.get("orderTerm"),
                        "estimated_commission": orders.get("estimatedCommission"),
                        "estimated_total_amount": orders.get("estimatedTotalAmount"),
                        "instruments": [],
                    }

                    if orders is not None and "Instrument" in orders:
                        for instrument in orders["Instrument"]:
                            instrument_info = {
                                "order_action": instrument.get("orderAction"),
                                "quantity": instrument.get("quantity"),
                                "symbol_description": instrument.get(
                                    "symbolDescription"
                                ),
                            }

                            if instrument is not None and "Product" in instrument:
                                instrument_info["symbol"] = instrument["Product"].get(
                                    "symbol"
                                )

                            order_info["instruments"].append(instrument_info)

                    result["preview_data"]["orders"].append(order_info)

                return result
            else:
                # Handle errors
                if (
                    "Error" in data
                    and "message" in data["Error"]
                    and data["Error"]["message"] is not None
                ):
                    return {"success": False, "error": data["Error"]["message"]}
                else:
                    return {
                        "success": False,
                        "error": "Preview Order API service error",
                    }
        else:
            # Handle errors
            if response is not None:
                try:
                    data = response.json()
                    if (
                        "Error" in data
                        and "message" in data["Error"]
                        and data["Error"]["message"] is not None
                    ):
                        return {"success": False, "error": data["Error"]["message"]}
                except:
                    pass
            return {"success": False, "error": "Preview Order API service error"}

    def place_order(self, order_params, preview_id):
        """
        Place an order after previewing it

        :param order_params: Dictionary containing order parameters
        :param preview_id: Preview ID from preview_order response
        :return: Dictionary containing order placement response or error information
        """

        # Validate order parameters
        if not self._validate_order_params(order_params):
            return {"success": False, "error": "Invalid order parameters"}

        if not preview_id:
            return {"success": False, "error": "Preview ID is required"}

        # Generate client order ID if not provided
        order = order_params.copy()
        if "client_order_id" not in order or not order["client_order_id"]:
            order["client_order_id"] = random.randint(1000000000, 9999999999)

        # URL for the API endpoint
        url = (
            self.base_url
            + "/v1/accounts/"
            + self.account["accountIdKey"]
            + "/orders/place.json"
        )

        # Add parameters and header information
        headers = {
            "Content-Type": "application/xml",
            "consumerKey": config["DEFAULT"]["CONSUMER_KEY"],
        }

        # Add payload for POST Request
        payload = """<PlaceOrderRequest>
                       <orderType>EQ</orderType>
                       <clientOrderId>{0}</clientOrderId>
                       <PreviewIds>
                           <previewId>{1}</previewId>
                       </PreviewIds>
                       <Order>
                           <allOrNone>false</allOrNone>
                           <priceType>{2}</priceType>
                           <orderTerm>{3}</orderTerm>
                           <marketSession>REGULAR</marketSession>
                           <stopPrice></stopPrice>
                           <limitPrice>{4}</limitPrice>
                           <Instrument>
                               <Product>
                                   <securityType>EQ</securityType>
                                   <symbol>{5}</symbol>
                               </Product>
                               <orderAction>{6}</orderAction>
                               <quantityType>QUANTITY</quantityType>
                               <quantity>{7}</quantity>
                           </Instrument>
                       </Order>
                   </PlaceOrderRequest>"""
        payload = payload.format(
            order["client_order_id"],
            preview_id,
            order["price_type"],
            order.get("order_term", "GOOD_FOR_DAY"),
            order.get("limit_price", ""),
            order["symbol"],
            order["order_action"],
            order["quantity"],
        )

        # Make API call for POST request
        response = self.session.post(
            url, header_auth=True, headers=headers, data=payload
        )
        logger.debug("Request Header: %s", response.request.headers)
        logger.debug("Request payload: %s", payload)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )
            data = response.json()

            result = {"success": True, "order_data": {}}

            if (
                data is not None
                and "PlaceOrderResponse" in data
                and "OrderIds" in data["PlaceOrderResponse"]
            ):
                result["order_data"]["order_ids"] = []
                for order_id in data["PlaceOrderResponse"]["OrderIds"]:
                    result["order_data"]["order_ids"].append(
                        {"order_id": order_id.get("orderId")}
                    )

            if (
                data is not None
                and "PlaceOrderResponse" in data
                and "Order" in data["PlaceOrderResponse"]
            ):
                result["order_data"]["orders"] = []
                for order_info in data["PlaceOrderResponse"]["Order"]:
                    order_details = {
                        "limit_price": order_info.get("limitPrice"),
                        "price_type": order_info.get("priceType"),
                        "order_term": order_info.get("orderTerm"),
                        "estimated_commission": order_info.get("estimatedCommission"),
                        "estimated_total_amount": order_info.get(
                            "estimatedTotalAmount"
                        ),
                        "instruments": [],
                    }

                    if order_info is not None and "Instrument" in order_info:
                        for instrument in order_info["Instrument"]:
                            instrument_info = {
                                "order_action": instrument.get("orderAction"),
                                "quantity": instrument.get("quantity"),
                                "symbol_description": instrument.get(
                                    "symbolDescription"
                                ),
                            }

                            if instrument is not None and "Product" in instrument:
                                instrument_info["symbol"] = instrument["Product"].get(
                                    "symbol"
                                )

                            order_details["instruments"].append(instrument_info)

                    result["order_data"]["orders"].append(order_details)

                return result
            else:
                # Handle errors
                if (
                    "Error" in data
                    and "message" in data["Error"]
                    and data["Error"]["message"] is not None
                ):
                    return {"success": False, "error": data["Error"]["message"]}
                else:
                    return {"success": False, "error": "Place Order API service error"}
        else:
            # Handle errors
            if response is not None:
                try:
                    data = response.json()
                    if (
                        "Error" in data
                        and "message" in data["Error"]
                        and data["Error"]["message"] is not None
                    ):
                        return {"success": False, "error": data["Error"]["message"]}
                except:
                    pass
            return {"success": False, "error": "Place Order API service error"}

    def cancel_order(self, order_id):
        """
        Cancel an existing order by order ID

        :param order_id: The order ID to cancel
        :return: Dictionary containing cancellation response or error information
        """

        if not order_id:
            return {"success": False, "error": "Order ID is required"}

        # URL for the API endpoint
        url = (
            self.base_url
            + "/v1/accounts/"
            + self.account["accountIdKey"]
            + "/orders/"
            + str(order_id)
            + "/cancel.json"
        )

        # Add parameters and header information
        headers = {
            "Content-Type": "application/xml",
            "consumerKey": config["DEFAULT"]["CONSUMER_KEY"],
        }

        # Add payload for PUT Request
        payload = """<CancelOrderRequest>
                       <orderId>{0}</orderId>
                   </CancelOrderRequest>""".format(
            order_id
        )

        # Make API call for PUT request
        response = self.session.put(
            url, header_auth=True, headers=headers, data=payload
        )
        logger.debug("Request Header: %s", response.request.headers)
        logger.debug("Request payload: %s", payload)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug(
                "Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True)
            )
            data = response.json()

            result = {"success": True, "cancellation_data": {}}

            if (
                data is not None
                and "CancelOrderResponse" in data
                and "orderId" in data["CancelOrderResponse"]
            ):
                result["cancellation_data"]["order_id"] = data["CancelOrderResponse"][
                    "orderId"
                ]
                result["cancellation_data"]["status"] = "cancelled"

                return result
            else:
                # Handle errors
                if (
                    "Error" in data
                    and "message" in data["Error"]
                    and data["Error"]["message"] is not None
                ):
                    return {"success": False, "error": data["Error"]["message"]}
                else:
                    return {"success": False, "error": "Cancel Order API service error"}
        else:
            # Handle errors
            if response is not None:
                try:
                    data = response.json()
                    if (
                        "Error" in data
                        and "message" in data["Error"]
                        and data["Error"]["message"] is not None
                    ):
                        return {"success": False, "error": data["Error"]["message"]}
                except:
                    pass
            return {"success": False, "error": "Cancel Order API service error"}

    def get_order_options(self):
        """
        Get available options for order parameters

        :return: Dictionary containing available options for creating orders
        """
        return {
            "price_types": ["MARKET", "LIMIT"],
            "order_terms": ["GOOD_FOR_DAY", "IMMEDIATE_OR_CANCEL", "FILL_OR_KILL"],
            "order_actions": ["BUY", "SELL", "BUY_TO_COVER", "SELL_SHORT"],
            "security_types": ["EQ"],  # Equity
            "quantity_types": ["QUANTITY"],
        }

    def view_orders(self):
        """
        Calls orders API to provide the details for the orders

        :param self: Pass in authenticated session and information on selected account
        :return: Dictionary containing all order categories with their data
        """
        # URL for the API endpoint
        url = (
            self.base_url
            + "/v1/accounts/"
            + self.account["accountIdKey"]
            + "/orders.json"
        )

        # Add parameters and header information
        headers = {"consumerkey": config["DEFAULT"]["CONSUMER_KEY"]}
        status_params = {
            "open": {"status": "OPEN"},
            "executed": {"status": "EXECUTED"},
            "individual_fills": {"status": "INDIVIDUAL_FILLS"},
            "cancelled": {"status": "CANCELLED"},
            "rejected": {"status": "REJECTED"},
            "expired": {"status": "EXPIRED"},
        }

        result = {
            "success": True,
            "orders": {
                "open": [],
                "executed": [],
                "individual_fills": [],
                "cancelled": [],
                "rejected": [],
                "expired": [],
            },
        }

        # Make API calls for each status
        for status_key, params in status_params.items():
            try:
                response = self.session.get(
                    url, header_auth=True, params=params, headers=headers
                )

                logger.debug("Request Header: %s", response.request.headers)
                logger.debug("Response Body: %s", response.text)

                if response.status_code == 200:
                    parsed = json.loads(response.text)
                    logger.debug(json.dumps(parsed, indent=4, sort_keys=True))
                    data = response.json()
                    result["orders"][status_key] = self.extract_orders_data(
                        data, status_key
                    )
                elif response.status_code == 204:
                    # No orders for this status
                    result["orders"][status_key] = []
                else:
                    logger.error(
                        f"Error fetching {status_key} orders: {response.status_code}"
                    )

            except Exception as e:
                logger.error(f"Exception while fetching {status_key} orders: {str(e)}")
                result["success"] = False
                result["error"] = f"Error fetching orders: {str(e)}"
                return result

        return result

    def extract_orders_data(self, response, status):
        """
        Extracts and formats order data from API response

        :param response: response object of a list of orders
        :param status: order status related to the response object
        :return: list of processed orders
        """
        orders_list = []
        if (
            response is not None
            and "OrdersResponse" in response
            and "Order" in response["OrdersResponse"]
        ):
            for order in response["OrdersResponse"]["Order"]:
                if order is not None and "OrderDetail" in order:
                    for details in order["OrderDetail"]:
                        if details is not None and "Instrument" in details:
                            for instrument in details["Instrument"]:
                                order_obj = {
                                    "order_id": order.get("orderId"),
                                    "order_type": order.get("orderType"),
                                    "price_type": details.get("priceType"),
                                    "order_term": details.get("orderTerm"),
                                    "limit_price": details.get("limitPrice"),
                                    "status": details.get("status"),
                                    "security_type": None,
                                    "symbol": None,
                                    "order_action": instrument.get("orderAction"),
                                    "quantity": instrument.get("orderedQuantity"),
                                    "filled_quantity": instrument.get("filledQuantity"),
                                    "average_execution_price": instrument.get(
                                        "averageExecutionPrice"
                                    ),
                                    "bid": (
                                        details.get("netBid")
                                        if status == "open"
                                        else None
                                    ),
                                    "ask": (
                                        details.get("netAsk")
                                        if status == "open"
                                        else None
                                    ),
                                    "net_price": (
                                        details.get("netPrice")
                                        if status == "open"
                                        else None
                                    ),
                                }

                                # Extract product information
                                if instrument is not None and "Product" in instrument:
                                    product = instrument["Product"]
                                    order_obj["security_type"] = product.get(
                                        "securityType"
                                    )
                                    order_obj["symbol"] = product.get("symbol")

                                # For individual fills, use filled quantity instead of ordered quantity
                                if status == "individual_fills" and instrument.get(
                                    "filledQuantity"
                                ):
                                    order_obj["quantity"] = instrument["filledQuantity"]

                                orders_list.append(order_obj)

        return orders_list
