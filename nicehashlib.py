from datetime import datetime
from time import mktime
import uuid
import hmac
import requests
import json
from hashlib import sha256
import optparse
import os
import guimain

class private_api:

    def __init__(self, host, organisation_id, key, secret, rigid, verbose=False):
        self.key = key
        self.secret = secret
        self.organisation_id = organisation_id
        self.host = host
        self.rigid = rigid
        self.verbose = verbose

    def request(self, method, path, query, body):

        xtime = self.get_epoch_ms_from_now()
        xnonce = str(uuid.uuid4())

        message = bytearray(self.key, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(str(xtime), 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(xnonce, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(self.organisation_id, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(method, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(path, 'utf-8')
        message += bytearray('\x00', 'utf-8')
        message += bytearray(query, 'utf-8')

        if body:
            body_json = json.dumps(body)
            message += bytearray('\x00', 'utf-8')
            message += bytearray(body_json, 'utf-8')

        digest = hmac.new(bytearray(self.secret, 'utf-8'), message, sha256).hexdigest()
        xauth = self.key + ":" + digest

        headers = {
            'X-Time': str(xtime),
            'X-Nonce': xnonce,
            'X-Auth': xauth,
            'Content-Type': 'application/json',
            'X-Organization-Id': self.organisation_id,
            'X-Request-Id': str(uuid.uuid4())
        }

        s = requests.Session()
        s.headers = headers

        url = self.host + path
        if query:
            url += '?' + query

        if self.verbose:
            print(method, url)

        if body:
            response = s.request(method, url, data=body_json)
        else:
            response = s.request(method, url)

        if response.status_code == 200:
            return response.json()
        elif response.content:
            msg='It seems that you have provided incorrect information about:\n1.Org id\n2.Key\n3.Secret\n4.Rigid\nPlease verify the above informations.'
            err='API Pull Error'
            guimain.nicehashapp.err_pop(err,msg)
            os.remove('config.ini')
            os._exit(1)
        else:
            raise Exception(str(response.status_code) + ": " + response.reason)

    def get_epoch_ms_from_now(self):
        now = datetime.now()
        now_ec_since_epoch = mktime(now.timetuple()) + now.microsecond / 1000000.0
        return int(now_ec_since_epoch * 1000)

    def algo_settings_from_response(self, algorithm, algo_response):
        algo_setting = None
        for item in algo_response['miningAlgorithms']:
            if item['algorithm'] == algorithm:
                algo_setting = item

        if algo_setting is None:
            raise Exception('Settings for algorithm not found in algo_response parameter')

        return algo_setting

    def get_accounts(self):
        return self.request('GET', '/main/api/v2/accounting/accounts2/', '', None)

    def get_accounts_for_currency(self, currency):
        return self.request('GET', '/main/api/v2/accounting/account2/' + currency, '', None)

    def get_withdrawal_addresses(self, currency, size, page):

        params = "currency={}&size={}&page={}".format(currency, size, page)

        return self.request('GET', '/main/api/v2/accounting/withdrawalAddresses/', params, None)

    def get_withdrawal_types(self):
        return self.request('GET', '/main/api/v2/accounting/withdrawalAddresses/types/', '', None)

    def withdraw_request(self, address_id, amount, currency):
        withdraw_data = {
            "withdrawalAddressId": address_id,
            "amount": amount,
            "currency": currency
        }
        return self.request('POST', '/main/api/v2/accounting/withdrawal/', '', withdraw_data)

    def get_my_active_orders(self, algorithm, market, limit):

        ts = self.get_epoch_ms_from_now()
        params = "algorithm={}&market={}&ts={}&limit={}&op=LT".format(algorithm, market, ts, limit)

        return self.request('GET', '/main/api/v2/hashpower/myOrders', params, None)

    def create_pool(self, name, algorithm, pool_host, pool_port, username, password):
        pool_data = {
            "name": name,
            "algorithm": algorithm,
            "stratumHostname": pool_host,
            "stratumPort": pool_port,
            "username": username,
            "password": password
        }
        return self.request('POST', '/main/api/v2/pool/', '', pool_data)

    def delete_pool(self, pool_id):
        return self.request('DELETE', '/main/api/v2/pool/' + pool_id, '', None)

    def get_my_pools(self, page, size):
        return self.request('GET', '/main/api/v2/pools/', '', None)

    def get_hashpower_orderbook(self, algorithm):
        return self.request('GET', '/main/api/v2/hashpower/orderBook/', 'algorithm=' + algorithm, None )
    
    def create_hashpower_order(self, market, type, algorithm, price, limit, amount, pool_id, algo_response):

        algo_setting = self.algo_settings_from_response(algorithm, algo_response)

        order_data = {
            "market": market,
            "algorithm": algorithm,
            "amount": amount,
            "price": price,
            "limit": limit,
            "poolId": pool_id,
            "type": type,
            "marketFactor": algo_setting['marketFactor'],
            "displayMarketFactor": algo_setting['displayMarketFactor']
        }
        return self.request('POST', '/main/api/v2/hashpower/order/', '', order_data)

    def cancel_hashpower_order(self, order_id):
        return self.request('DELETE', '/main/api/v2/hashpower/order/' + order_id, '', None)

    def refill_hashpower_order(self, order_id, amount):
        refill_data = {
            "amount": amount
        }
        return self.request('POST', '/main/api/v2/hashpower/order/' + order_id + '/refill/', '', refill_data)

    def set_price_hashpower_order(self, order_id, price, algorithm, algo_response):

        algo_setting = self.algo_settings_from_response(algorithm, algo_response)

        price_data = {
            "price": price,
            "marketFactor": algo_setting['marketFactor'],
            "displayMarketFactor": algo_setting['displayMarketFactor']
        }
        return self.request('POST', '/main/api/v2/hashpower/order/' + order_id + '/updatePriceAndLimit/', '',
                            price_data)

    def set_limit_hashpower_order(self, order_id, limit, algorithm, algo_response):
        algo_setting = self.algo_settings_from_response(algorithm, algo_response)
        limit_data = {
            "limit": limit,
            "marketFactor": algo_setting['marketFactor'],
            "displayMarketFactor": algo_setting['displayMarketFactor']
        }
        return self.request('POST', '/main/api/v2/hashpower/order/' + order_id + '/updatePriceAndLimit/', '',
                            limit_data)

    def set_price_and_limit_hashpower_order(self, order_id, price, limit, algorithm, algo_response):
        algo_setting = self.algo_settings_from_response(algorithm, algo_response)

        price_data = {
            "price": price,
            "limit": limit,
            "marketFactor": algo_setting['marketFactor'],
            "displayMarketFactor": algo_setting['displayMarketFactor']
        }
        return self.request('POST', '/main/api/v2/hashpower/order/' + order_id + '/updatePriceAndLimit/', '',
                            price_data)

    def get_my_exchange_orders(self, market):
        return self.request('GET', '/exchange/api/v2/myOrders', 'market=' + market, None)
    
    def rig_stats(self):
        return self.request('GET', '/main/api/v2/mining/rig2/'+self.rigid,'', None)

    def get_my_exchange_trades(self, market):
        return self.request('GET','/exchange/api/v2/myTrades', 'market=' + market, None)

    def create_exchange_limit_order(self, market, side, quantity, price):
        query = "market={}&side={}&type=limit&quantity={}&price={}".format(market, side, quantity, price)
        return self.request('POST', '/exchange/api/v2/order', query, None)

    def create_exchange_buy_market_order(self, market, quantity):
        query = "market={}&side=buy&type=market&secQuantity={}".format(market, quantity)
        return self.request('POST', '/exchange/api/v2/order', query, None)

    def create_exchange_sell_market_order(self, market, quantity):
        query = "market={}&side=sell&type=market&quantity={}".format(market, quantity)
        return self.request('POST', '/exchange/api/v2/order', query, None)

    def cancel_exchange_order(self, market, order_id):
        query = "market={}&orderId={}".format(market, order_id)
        return self.request('DELETE', '/exchange/api/v2/order', query, None)


if __name__ == "__main__":
    parser = optparse.OptionParser()

    parser.add_option('-b', '--base_url', dest="base", help="Api base url", default="https://api2.nicehash.com")
    parser.add_option('-o', '--organization_id', dest="org", help="Organization id")
    parser.add_option('-k', '--key', dest="key", help="Api key")
    parser.add_option('-s', '--secret', dest="secret", help="Secret for api key")
    parser.add_option('-m', '--method', dest="method", help="Method for request", default="GET")
    parser.add_option('-p', '--path', dest="path", help="Path for request", default="/")
    parser.add_option('-q', '--params', dest="params", help="Parameters for request")
    parser.add_option('-d', '--body', dest="body", help="Body for request")

    options, args = parser.parse_args()

    private_api = private_api(options.base, options.org, options.key, options.secret, options.rigid)

    params = ''
    if options.params is not None:
        params = options.params

    try:
        response = private_api.request(options.method, options.path, params, options.body)
    except Exception as ex:
        print("Unexpected error:", ex)
        exit(1)

    print(response)
    exit(0)