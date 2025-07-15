import json
import logging
from logging.handlers import RotatingFileHandler
import configparser
import random
import re

# loading configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# logger settings
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler("python_client.log", maxBytes=5 * 1024 * 1024, backupCount=3)
FORMAT = "%(asctime)-15s %(message)s"
fmt = logging.Formatter(FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
handler.setFormatter(fmt)
logger.addHandler(handler)


class Order:

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.account = {}

    def set_account(self, account):
        """
        Set the account for order operations
        :param account: Account dictionary with accountIdKey and other details
        """
        self.account = account

    def preview_order(self, order_params):
        """
        Call preview order API based on provided order parameters

        :param order_params: Dictionary containing order parameters
        :return: Dictionary containing preview order response or None if error
        """
        if not order_params:
            return None

        # URL for the API endpoint
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/orders/preview.json"

        # Add parameters and header information
        headers = {"Content-Type": "application/xml", "consumerKey": config["DEFAULT"]["CONSUMER_KEY"]}

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
        payload = payload.format(order_params["client_order_id"], order_params["price_type"], order_params["order_term"],
                                 order_params["limit_price"], order_params["symbol"], order_params["order_action"], order_params["quantity"])

        # Make API call for POST request
        response = self.session.post(url, header_auth=True, headers=headers, data=payload)
        logger.debug("Request Header: %s", response.request.headers)
        logger.debug("Request payload: %s", payload)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            data = response.json()
            
            result = {"success": True, "preview_data": {}}

            if data is not None and "PreviewOrderResponse" in data and "PreviewIds" in data["PreviewOrderResponse"]:
                result["preview_data"]["preview_ids"] = []
                for previewids in data["PreviewOrderResponse"]["PreviewIds"]:
                    result["preview_data"]["preview_ids"].append(previewids["previewId"])

            if data is not None and "PreviewOrderResponse" in data and "Order" in data["PreviewOrderResponse"]:
                result["preview_data"]["orders"] = []
                for orders in data["PreviewOrderResponse"]["Order"]:
                    order_details = {}
                    if "limitPrice" in orders:
                        order_details["limitPrice"] = orders["limitPrice"]
                    if "priceType" in orders:
                        order_details["priceType"] = orders["priceType"]
                    if "orderTerm" in orders:
                        order_details["orderTerm"] = orders["orderTerm"]
                    if "estimatedCommission" in orders:
                        order_details["estimatedCommission"] = orders["estimatedCommission"]
                    if "estimatedTotalAmount" in orders:
                        order_details["estimatedTotalAmount"] = orders["estimatedTotalAmount"]
                    
                    if orders is not None and "Instrument" in orders:
                        order_details["instruments"] = []
                        for instrument in orders["Instrument"]:
                            inst_details = {}
                            if instrument is not None and "orderAction" in instrument:
                                inst_details["orderAction"] = instrument["orderAction"]
                            if instrument is not None and "quantity" in instrument:
                                inst_details["quantity"] = instrument["quantity"]
                            if instrument is not None and "Product" in instrument \
                                    and "symbol" in instrument["Product"]:
                                inst_details["symbol"] = instrument["Product"]["symbol"]
                            if instrument is not None and "symbolDescription" in instrument:
                                inst_details["symbolDescription"] = instrument["symbolDescription"]
                            order_details["instruments"].append(inst_details)
                    result["preview_data"]["orders"].append(order_details)
            
            return result
        else:
            # Handle errors
            data = response.json()
            error_msg = "Preview Order API service error"
            if 'Error' in data and 'message' in data["Error"] and data["Error"]["message"] is not None:
                error_msg = data["Error"]["message"]
            logger.debug("Preview Order error: %s", error_msg)
            return {"success": False, "error": error_msg}


    def parse_orders(self, response, status):
        """
        Parses and formats a list of orders

        :param response: response object of a list of orders
        :param status: order status related to the response object
        :return: a list of parsed orders
        """
        orders_list = []
        if response is not None and "OrdersResponse" in response and "Order" in response["OrdersResponse"]:
            for order in response["OrdersResponse"]["Order"]:
                if order is not None and "OrderDetail" in order:
                    for details in order["OrderDetail"]:
                        if details is not None and "Instrument" in details:
                            for instrument in details["Instrument"]:
                                order_obj = {
                                    "order_id": order.get("orderId"),
                                    "price_type": details.get("priceType"),
                                    "order_term": details.get("orderTerm"),
                                    "order_type": order.get("orderType"),
                                    "security_type": instrument.get("Product", {}).get("securityType"),
                                    "symbol": instrument.get("Product", {}).get("symbol"),
                                    "order_action": instrument.get("orderAction"),
                                    "quantity": instrument.get("orderedQuantity"),
                                    "limit_price": details.get("limitPrice"),
                                    "status": details.get("status")
                                }
                                
                                # Add status-specific fields
                                if status == "Open":
                                    order_obj["bid"] = details.get("netBid")
                                    order_obj["ask"] = details.get("netAsk")
                                    order_obj["net_price"] = details.get("netPrice")
                                elif status == "indiv_fills":
                                    order_obj["filled_quantity"] = instrument.get("filledQuantity")
                                elif status not in ["open", "expired", "rejected"]:
                                    order_obj["average_execution_price"] = instrument.get("averageExecutionPrice")
                                
                                orders_list.append(order_obj)
        return orders_list



    def cancel_order(self, order_id):
        """
        Calls cancel order API to cancel an existing order
        
        :param order_id: The order ID to cancel
        :return: Dictionary containing cancellation result
        """
        if not order_id:
            return {"success": False, "error": "Order ID is required"}

        # URL for the API endpoint
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/orders/cancel.json"

        # Add parameters and header information
        headers = {"Content-Type": "application/xml", "consumerKey": config["DEFAULT"]["CONSUMER_KEY"]}

        # Add payload for POST Request
        payload = """<CancelOrderRequest>
                        <orderId>{0}</orderId>
                    </CancelOrderRequest>
                   """
        payload = payload.format(order_id)

        # Add payload for PUT Request
        response = self.session.put(url, header_auth=True, headers=headers, data=payload)
        logger.debug("Request Header: %s", response.request.headers)
        logger.debug("Request payload: %s", payload)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            data = response.json()
            if data is not None and "CancelOrderResponse" in data \
                    and "orderId" in data["CancelOrderResponse"]:
                return {
                    "success": True,
                    "cancelled_order_id": data["CancelOrderResponse"]["orderId"],
                    "message": f"Order #{data['CancelOrderResponse']['orderId']} successfully cancelled"
                }
            else:
                # Handle errors
                logger.debug("Response Headers: %s", response.headers)
                logger.debug("Response Body: %s", response.text)
                data = response.json()
                error_msg = "Cancel Order API service error"
                if 'Error' in data and 'message' in data["Error"] \
                        and data["Error"]["message"] is not None:
                    error_msg = data["Error"]["message"]
                return {"success": False, "error": error_msg}
        else:
            # Handle errors
            logger.debug("Response Headers: %s", response.headers)
            logger.debug("Response Body: %s", response.text)
            data = response.json()
            error_msg = "Cancel Order API service error"
            if 'Error' in data and 'message' in data["Error"] and data["Error"]["message"] is not None:
                error_msg = data["Error"]["message"]
            return {"success": False, "error": error_msg}

    def view_orders(self):
        """
        Calls orders API to provide the details for the orders

        :return: Dictionary containing orders data organized by status
        """
        # URL for the API endpoint
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/orders.json"

        # Add parameters and header information
        headers = {"consumerkey": config["DEFAULT"]["CONSUMER_KEY"]}
        params_open = {"status": "OPEN"}
        params_executed = {"status": "EXECUTED"}
        params_indiv_fills = {"status": "INDIVIDUAL_FILLS"}
        params_cancelled = {"status": "CANCELLED"}
        params_rejected = {"status": "REJECTED"}
        params_expired = {"status": "EXPIRED"}

        # Make API call for GET request
        response_open = self.session.get(url, header_auth=True, params=params_open, headers=headers)
        response_executed = self.session.get(url, header_auth=True, params=params_executed, headers=headers)
        response_indiv_fills = self.session.get(url, header_auth=True, params=params_indiv_fills, headers=headers)
        response_cancelled = self.session.get(url, header_auth=True, params=params_cancelled, headers=headers)
        response_rejected = self.session.get(url, header_auth=True, params=params_rejected, headers=headers)
        response_expired = self.session.get(url, header_auth=True, params=params_expired, headers=headers)

        result = {
            "open_orders": [],
            "executed_orders": [],
            "individual_fills_orders": [],
            "cancelled_orders": [],
            "rejected_orders": [],
            "expired_orders": []
        }

        # Open orders
        logger.debug("Request Header: %s", response_open.request.headers)
        logger.debug("Response Body: %s", response_open.text)

        if response_open.status_code == 200:
            parsed = json.loads(response_open.text)
            logger.debug(json.dumps(parsed, indent=4, sort_keys=True))
            data = response_open.json()
            result["open_orders"] = self.parse_orders(data, "open")

        # Executed orders
        logger.debug("Request Header: %s", response_executed.request.headers)
        logger.debug("Response Body: %s", response_executed.text)

        if response_executed.status_code == 200:
            parsed = json.loads(response_executed.text)
            logger.debug(json.dumps(parsed, indent=4, sort_keys=True))
            data = response_executed.json()
            result["executed_orders"] = self.parse_orders(data, "executed")

        # Individual fills orders
        logger.debug("Request Header: %s", response_indiv_fills.request.headers)
        logger.debug("Response Body: %s", response_indiv_fills.text)

        if response_indiv_fills.status_code == 200:
            parsed = json.loads(response_indiv_fills.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            data = response_indiv_fills.json()
            result["individual_fills_orders"] = self.parse_orders(data, "indiv_fills")

        # Cancelled orders
        logger.debug("Request Header: %s", response_cancelled.request.headers)
        logger.debug("Response Body: %s", response_cancelled.text)

        if response_cancelled.status_code == 200:
            parsed = json.loads(response_cancelled.text)
            logger.debug(json.dumps(parsed, indent=4, sort_keys=True))
            data = response_cancelled.json()
            result["cancelled_orders"] = self.parse_orders(data, "cancelled")

        # Rejected orders
        logger.debug("Request Header: %s", response_rejected.request.headers)
        logger.debug("Response Body: %s", response_rejected.text)

        if response_rejected.status_code == 200:
            parsed = json.loads(response_rejected.text)
            logger.debug(json.dumps(parsed, indent=4, sort_keys=True))
            data = response_rejected.json()
            result["rejected_orders"] = self.parse_orders(data, "rejected")

        # Expired orders
        if response_expired.status_code == 200:
            parsed = json.loads(response_expired.text)
            logger.debug(json.dumps(parsed, indent=4, sort_keys=True))
            data = response_expired.json()
            result["expired_orders"] = self.parse_orders(data, "expired")

        return result
