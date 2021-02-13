import requests
import json

# https://github.com/lolokraus/DegiroAPI

class DeGiro:
    __LOGIN_URL = 'https://trader.degiro.nl/login/secure/login'
    __CONFIG_URL = 'https://trader.degiro.nl/login/secure/config'

    __LOGOUT_URL = 'https://trader.degiro.nl/trading/secure/logout'

    __CLIENT_INFO_URL = 'https://trader.degiro.nl/pa/secure/client'

    __GET_STOCKS_URL = 'https://trader.degiro.nl/products_s/secure/v5/stocks'
    __PRODUCT_SEARCH_URL = 'https://trader.degiro.nl/product_search/secure/v5/products/lookup'
    __PRODUCT_INFO_URL = 'https://trader.degiro.nl/product_search/secure/v5/products/info'
    __TRANSACTIONS_URL = 'https://trader.degiro.nl/reporting/secure/v4/transactions'
    __ORDERS_URL = 'https://trader.degiro.nl/reporting/secure/v4/order-history'

    __PLACE_ORDER_URL = 'https://trader.degiro.nl/trading/secure/v5/checkOrder'
    __ORDER_URL = 'https://trader.degiro.nl/trading/secure/v5/order/'

    __DATA_URL = 'https://trader.degiro.nl/trading/secure/v5/update/'
    __PRICE_DATA_URL = 'https://charting.vwdservices.com/hchart/v1/deGiro/data.js'

    __GET_REQUEST = 0
    __POST_REQUEST = 1
    __DELETE_REQUEST = 2

    client_token = any
    session_id = any
    client_info = any
    confirmation_id = any
    client_username = None

    def login(self, username, password):
        self.client_username = username
        login_payload = {
            'username': username,
            'password': password,
            'isPassCodeReset': False,
            'isRedirectToMobile': False
        }
        login_response = self.__request(DeGiro.__LOGIN_URL, None, login_payload, request_type=DeGiro.__POST_REQUEST,
                                        error_message='Could not login.')
        self.session_id = login_response['sessionId']
        client_info_payload = {'sessionId': self.session_id}
        client_info_response = self.__request(DeGiro.__CLIENT_INFO_URL, None, client_info_payload,
                                              error_message='Could not get client info.')
        self.client_info = ClientInfo(client_info_response['data'])

        cookie = {
            'JSESSIONID': self.session_id
        }

        client_token_response = self.__request(DeGiro.__CONFIG_URL, cookie=cookie, request_type=DeGiro.__GET_REQUEST,
                                               error_message='Could not get client config.')
        self.client_token = client_token_response['data']['clientId']

        return client_info_response

    def logout(self):
        logout_payload = {
            'intAccount': self.client_info.account_id,
            'sessionId': self.session_id,
        }
        self.__request(DeGiro.__LOGOUT_URL + ';jsessionid=' + self.session_id, None, logout_payload,
                       error_message='Could not log out')

    @staticmethod
    def __request(url, cookie=None, payload=None, headers=None, data=None, post_params=None, request_type=__GET_REQUEST,
                  error_message='An error occurred.'):

        if request_type == DeGiro.__DELETE_REQUEST:
            response = requests.delete(url, json=payload)
        elif request_type == DeGiro.__GET_REQUEST and cookie:
            response = requests.get(url, cookies=cookie)
        elif request_type == DeGiro.__GET_REQUEST:
            response = requests.get(url, params=payload)
        elif request_type == DeGiro.__POST_REQUEST and headers and data:
            response = requests.post(url, headers=headers, params=payload, data=data)
        elif request_type == DeGiro.__POST_REQUEST and post_params:
            response = requests.post(url, params=post_params, json=payload)
        elif request_type == DeGiro.__POST_REQUEST:
            response = requests.post(url, json=payload)
        else:
            raise Exception(f'Unknown request type: {request_type}')

        # print(json.dumps(response.json(), indent=4, sort_keys=True))
        if response.status_code == 200 or response.status_code == 201:
            try:
                return response.json()
            except:
                return "No data"
        else:
            raise Exception(f'{error_message} Response: {response.text}')

    def search_products(self, search_text, limit=1):
        product_search_payload = {
            'searchText': search_text,
            'limit': limit,
            'offset': 0,
            'intAccount': self.client_info.account_id,
            'sessionId': self.session_id
        }
        return self.__request(DeGiro.__PRODUCT_SEARCH_URL, None, product_search_payload,
                              error_message='Could not get products.')['products']

    def product_info(self, product_id):
        product_info_payload = {
            'intAccount': self.client_info.account_id,
            'sessionId': self.session_id
        }
        return self.__request(DeGiro.__PRODUCT_INFO_URL, None, product_info_payload,
                              headers={'content-type': 'application/json'},
                              data=json.dumps([str(product_id)]),
                              request_type=DeGiro.__POST_REQUEST,
                              error_message='Could not get product info.')['data'][str(product_id)]


    @staticmethod
    def filtercashfunds(cashfunds):
        data = []
        for item in cashfunds['cashFunds']['value']:
            if item['value'][2]['value'] != 0:
                data.append(item['value'][1]['value'] + " " + str(item['value'][2]['value']))
        return data

    @staticmethod
    def filterportfolio(portfolio, filter_zero=None):
        data = []
        data_non_zero = []
        for item in portfolio['portfolio']['value']:
            positionType = size = price = value = breakEvenPrice = None
            for i in item['value']:
                size = i['value'] if i['name'] == 'size' else size
                positionType = i['value'] if i['name'] == 'positionType' else positionType
                price = i['value'] if i['name'] == 'price' else price
                value = i['value'] if i['name'] == 'value' else value
                breakEvenPrice = i['value'] if i['name'] == 'breakEvenPrice' else breakEvenPrice
            data.append({
                "id": item['id'],
                "positionType": positionType,
                "size": size,
                "price": price,
                "value": value,
                "breakEvenPrice": breakEvenPrice
            })
        if filter_zero:
            for d in data:
                if d['size'] != 0.0:
                    data_non_zero.append(d)
            return data_non_zero
        else:
            return data

    def getdata(self, datatype, filter_zero=None):
        data_payload = {
            datatype: 0
        }

        if datatype == Data.Type.CASHFUNDS:
            return self.filtercashfunds(
                self.__request(DeGiro.__DATA_URL + str(self.client_info.account_id) + ';jsessionid=' + self.session_id,
                               None,
                               data_payload,
                               error_message='Could not get data'))
        elif datatype == Data.Type.PORTFOLIO:
            return self.filterportfolio(
                self.__request(DeGiro.__DATA_URL + str(self.client_info.account_id) + ';jsessionid=' + self.session_id,
                               None,
                               data_payload,
                               error_message='Could not get data'), filter_zero)
        elif datatype == Data.Type.RAW_PORTFOLIO:
            return self.__request(DeGiro.__DATA_URL + str(self.client_info.account_id) + ';jsessionid=' + self.session_id,
                                  None,
                                  {Data.Type.PORTFOLIO: 0},
                                  error_message='Could not get data')
        else:
            return self.__request(
                DeGiro.__DATA_URL + str(self.client_info.account_id) + ';jsessionid=' + self.session_id, None,
                data_payload,
                error_message='Could not get data')

    def real_time_price(self, product_id, interval):
        vw_id = self.product_info(product_id)['vwdId']
        tmp = vw_id
        try:
            int(tmp)
        except:
            vw_id = self.product_info(product_id)['vwdIdSecondary']

        price_payload = {
            'requestid': 1,
            'period': interval,
            'series': ['issueid:' + vw_id, 'price:issueid:' + vw_id],
            'userToken': self.client_token
        }

        return self.__request(DeGiro.__PRICE_DATA_URL, None, price_payload,
                             error_message='Could not get real time price')['series']

    def get_stock_list(self, indexId, stockCountryId):
        stock_list_params = {
            'indexId': indexId,
            'stockCountryId': stockCountryId,
            'offset': 0,
            'limit': None,
            'requireTotal': "true",
            'sortColumns': "name",
            'sortTypes': "asc",
            'intAccount': self.client_info.account_id,
            'sessionId': self.session_id
        }
        return \
            self.__request(DeGiro.__GET_STOCKS_URL, None, stock_list_params, error_message='Could not get stock list')[
                'products']

class ClientInfo:
    def __init__(self, client_info):
        self.__account_id = client_info['intAccount']
        self.__username = client_info['username']
        self.__first_name = client_info['firstContact']['firstName']
        self.__last_name = client_info['firstContact']['lastName']
        self.__email = client_info['email']

    @property
    def account_id(self):
        return self.__account_id

    @property
    def username(self):
        return self.__username

    @property
    def first_name(self):
        return self.__first_name

    @property
    def last_name(self):
        return self.__last_name

    @property
    def email(self):
        return self.__email

class Data:
    class Type:
        PORTFOLIO = 'portfolio'
        CASHFUNDS = 'cashFunds'
        RAW_PORTFOLIO = 'raw_portfolio'