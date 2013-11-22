import requests
import time
import hmac
import hashlib
import sys
import collections
import time

class public():
    def __init__(self, rootUrl=None, proxydict=None):
        self.proxydict = proxydict
        if rootUrl:
            self.rootUrl = rootUrl
        else:
            self.rootUrl = "https://www.bitstamp.net"

    def ticker(self):
        """
        Return ticker output
        """
        r = limiter.get(self.rootUrl + "/api/ticker/", proxies=self.proxydict)
        if r.status_code == 200:
            return r.content
        else:
            r.raise_for_status()

    def order_book(self, group=True):
        """
        Returns "bids" and "asks".
        """
        params = {'group': group}

        r = limiter.get(self.rootUrl + "/api/order_book/", params=params, proxies=self.proxydict)
        if r.status_code == 200:
            return r.content
        else:
            r.raise_for_status()

    def transactions(self, timedelta_secs=86400):
        """
        Returns transactions for the last 'timedelta' seconds
        """
        params = {'timedelta': timedelta_secs}

        r = limiter.get(self.rootUrl + "/api/transactions/", params=params, proxies=self.proxydict)
        if r.status_code == 200:
            return r.content
        else:
            r.raise_for_status()

    def bitinstant_reserves(self):
        """
        Returns {'usd': 'Bitinstant USD reserves'}
        """
        r = limiter.get(self.rootUrl + "/api/bitinstant/", proxies=self.proxydict)
        if r.status_code == 200:
            return r.content
        else:
            r.raise_for_status()

    def conversion_rate_usd_eur(self):
        """
        Returns {'buy': 'buy conversion rate', 'sell': 'sell conversion rate'}
        """
        r = limiter.get(self.rootUrl + "/api/eur_usd/", proxies=self.proxydict)
        if r.status_code == 200:
            return r.content
        else:
            r.raise_for_status()


class trading():
    def __init__(self, username, key, secret, proxydict=None):
        self.proxydict = proxydict
        self.username = username
        self.key = key
        self.secret = secret
        self.nonce = int(time.time())
        
    def get_params(self):
        params = {}
        params['key'] = self.key
        msg = str(self.nonce) + self.username + self.key

        if sys.version_info.major == 2:
            signature = hmac.new(self.secret, msg=msg, digestmod=hashlib.sha256).hexdigest().upper()
        else:
            signature = hmac.new(str.encode(self.secret), msg=str.encode(msg), digestmod=hashlib.sha256).hexdigest()\
                .upper()
        params['signature'] = signature
        params['nonce'] = self.nonce
        self.nonce += 1
        return params

    def account_balance(self):
        """
        Returns
        {u'btc_reserved': u'0',
         u'fee': u'0.5000',
         u'btc_available': u'2.30856098',
         u'usd_reserved': u'0',
         u'btc_balance': u'2.30856098',
         u'usd_balance': u'114.64',
         u'usd_available': u'114.64'}
        """
        params = self.get_params()
        r = limiter.post(self.rootUrl + "/api/balance/", data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()

    def user_transactions(self, offset=0, limit=100, descending=True):
        """
        Returns descending list of transactions. Every transaction contains
        {u'usd': u'-39.25',
         u'datetime': u'2013-03-26 18:49:13',
         u'fee': u'0.20', u'btc': u'0.50000000',
         u'type': 2,
         u'id': 213642}
        """
        params = self.get_params()
        params['offset'] = offset
        params['limit'] = limit
        if descending:
            params['sort'] = "desc"
        else:
            params['sort'] = "asc"

        r = limiter.post(self.rootUrl + "/api/user_transactions/", data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()

    def open_orders(self):
        """
        Returns list of open orders.
        """
        params = self.get_params()
        r = limiter.post(self.rootUrl + "/api/open_orders/", data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()

    def cancel_order(self, order_id):
        """
        Cancel the order specified by order_id
        Returns True if order was successfully canceled,
        otherwise tuple (False, msg) like (False, u'Order not found')
        """
        params = self.get_params()
        params['id'] = order_id
        r = limiter.post(self.rootUrl + "/api/cancel_order/", data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if r.content == u'true':
                return True
            else:
                return False, r.json()['error']
        else:
            r.raise_for_status()

    def buy_limit_order(self, amount, price):
        """
        Order to buy amount of bitcoins for specified price
        """
        params = self.get_params()
        params['amount'] = amount
        params['price'] = price

        r = limiter.post(self.rootUrl + "/api/buy/", data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()

    def sell_limit_order(self, amount, price):
        """
        Order to buy amount of bitcoins for specified price
        """
        params = self.get_params()
        params['amount'] = amount
        params['price'] = price

        r = limiter.post(self.rootUrl + "/api/sell/", data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()
            
    def check_bitstamp_code(self, code):
        """
        Returns USD and BTC amount included in given bitstamp code.
        """
        params = self.get_params()
        params['code'] = code
        r = limiter.post(self.rootUrl + "/api/check_code/", data=params,
                          proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()
            
    def redeem_bitstamp_code(self, code):
        """
        Returns USD and BTC amount added to user's account.
        """
        params = self.get_params()
        params['code'] = code
        r = limiter.post(self.rootUrl + "/api/redeem_code/", data=params,
                          proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()
            
    def withdrawal_requests(self):
        """
        Returns list of withdrawal requests.
        """
        params = self.get_params()
        r = limiter.post(self.rootUrl + "/api/withdrawal_requests/", data=params,
                          proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()            

    def bitcoin_withdrawal(self, amount, address):
        """
        Send bitcoins to another bitcoin wallet specified by address
        """
        params = self.get_params()
        params['amount'] = amount
        params['address'] = address

        r = limiter.post(self.rootUrl + "/api/bitcoin_withdrawal/", data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if r.content == u'true':
                return True
            else:
                return False, r.json()['error']
        else:
            r.raise_for_status()

    def bitcoin_deposit_address(self):
        """
        Returns bitcoin deposit address as unicode string
        """
        params = self.get_params()
        r = limiter.post(self.rootUrl + "/api/bitcoin_deposit_address/", data=params,
                          proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()

    def unconfirmed_bitcoin_deposits(self):
        """
        Returns unconfirmed bitcoin transactions. Each transaction is represented:
        amount - bitcoin amount
        address - deposit address used
        confirmations - number of confirmations
        """
        params = self.get_params()
        r = limiter.post(self.rootUrl + "/api/unconfirmed_btc/", data=params,
                          proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()
            
    def ripple_withdrawal(self, amount, address, currency):
        """
        Returns true if successful
        """
        params = self.get_params()
        params['amount'] = amount
        params['address'] = address
        params['currency'] = currency

        r = limiter.post(self.rootUrl + "/api/ripple_withdrawal/", data=params, proxies=self.proxydict)
        if r.status_code == 200:
            if r.content == u'true':
                return True
            else:
                return False, r.json()['error']
        else:
            r.raise_for_status()

    def ripple_deposit_address(self):
        """
        Returns ripple deposit address as unicode string
        """
        params = self.get_params()
        r = limiter.post(self.rootUrl + "/api/ripple_address/", data=params,
                          proxies=self.proxydict)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.content
        else:
            r.raise_for_status()

class LimiterException(Exception):
    def __init__(self, msg, timeToWait):
        Exception.__init__(self, msg)
        self.timeToWait = timeToWait

class Limiter():
    def __init__(self, limit=True):
        # as specified by bitstamp api:
        self.requestsLimitNo = 600  # we limit to 600 requests
        self.requestsLimitInterval = 600 # 600s == 10 minutes
        # enable/disable limiting boolean var:
        self.limit = limit
        # some internals:
        self.session = requests.Session()
        self.dequeue = collections.deque(maxlen=self.requestsLimitNo)

    def intervalWithinLimit(self, timeA, timeB):
        ''' returns True if inteval fits within the limit(if the interval is > 10min). returns False otherwise '''
        if abs(timeA - timeB) > self.requestsLimitInterval:
            return True
        else:
            return False

    def _checkLimit(self):
        # if limiting is disabled, we just return
        if not self.limit:
            return

        currTime = time.time()
        # if there is still space left(number of requests<=600), we just add current time
        if len(self.dequeue) < self.dequeue.maxlen:
            self.dequeue.append(currTime)
            return

        # else, we need to check, whether we didn't make too many requests
        lastTimestamp = self.dequeue.popleft()

        # if the interval is > 600s, we pop it from left, add curr time and return as success
        if self.intervalWithinLimit(currTime, lastTimestamp):
            self.dequeue.append(currTime)
            return

        # else we don't fit within the limit, so we throw exception
        self.dequeue.appendleft(lastTimestamp)
        timeToWait = self.requestsLimitInterval - (currTime - lastTimestamp)
        raise LimiterException("Sent more than " + str(self.requestsLimitNo) + " requests in last:" + str(self.requestsLimitInterval) + " seconds. Wait for: " + str(timeToWait) + "seconds", timeToWait)

    def get(self, *args, **kwargs):
        self._checkLimit()
        return self.session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self._checkLimit()
        return self.session.post(*args, **kwargs)

limiter = Limiter(limit=True)
limiter.limit = True  # set to False from your program to disable limiting
