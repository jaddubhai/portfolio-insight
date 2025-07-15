from __future__ import print_function
import webbrowser
import configparser
from enum import Enum
from rauth import OAuth1Service

from accounts import Accounts
from market import Market
from order import Order

class KeyType(Enum):
    SANDBOX = "sandbox"
    LIVE = "live"

def oauth(key_type: KeyType = KeyType.SANDBOX):
    """Allows user authorization for the sample application with OAuth 1"""

    # loading configuration file
    config = configparser.ConfigParser()
    config.read('config.ini')
    print(config.defaults())

    etrade = OAuth1Service(
        name="etrade",
        consumer_key=config["DEFAULT"]["CONSUMER_KEY"],
        consumer_secret=config["DEFAULT"]["CONSUMER_SECRET"],
        request_token_url="https://api.etrade.com/oauth/request_token",
        access_token_url="https://api.etrade.com/oauth/access_token",
        authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
        base_url="https://api.etrade.com"
    )

    if key_type == KeyType.SANDBOX:
        base_url = config["DEFAULT"]["SANDBOX_BASE_URL"]
    elif key_type == KeyType.LIVE:
        base_url = config["DEFAULT"]["PROD_BASE_URL"]

    # Step 1: Get OAuth 1 request token and secret
    request_token, request_token_secret = etrade.get_request_token(
        params={"oauth_callback": "oob", "format": "json"})

    # Step 2: Go through the authentication flow. Login to E*TRADE.
    # After you login, the page will provide a verification code to enter.
    authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
    webbrowser.open(authorize_url)
    text_code = input("Please accept agreement and enter verification code from browser: ")

    # Step 3: Exchange the authorized request token for an authenticated OAuth 1 session
    session = etrade.get_auth_session(request_token,
                                  request_token_secret,
                                  params={"oauth_verifier": text_code})

    return base_url, session

def account_instance(base_url: str, session):
    return Accounts(session, base_url)

def market_instance(base_url: str, session):
    return Market(session, base_url) 

def order_instance(base_url: str, session):
    return Order(session, base_url)
