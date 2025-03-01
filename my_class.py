# Original Author: nedludd0
# Original Source: https://raw.githubusercontent.com/nedludd0/binance-exchange-python-api/master/my_class.py

# Mathematical
from decimal import getcontext, ROUND_DOWN, Decimal
import math

# Logs
import traceback
from pprint import pprint

# Python Binance Lib
from binance.client import Client, BinanceAPIException

# My
import utility

class BinanceAPI:

    def __init__(self, p_api_pub_key = None, p_api_secret_key = None, p_symbol_first = None, p_symbol_second = None, p_wallet = None):

        # Symbol
        if p_wallet:
            self.wallet = p_wallet.lower()
        else:
            self.wallet = 'spot'
        if p_symbol_first:
            self.symbol_first = p_symbol_first.upper()
        if p_symbol_second:
            self.symbol_second = p_symbol_second.upper()
        if p_symbol_first and p_symbol_second:
            self.symbol = f"{p_symbol_first}{p_symbol_second}".upper()

        # Working
        self.client_builded = None
        self.client         = None

        # Build Client
        self.request_timeout    = 20
        self.client_builded     = self.build_client(p_api_pub_key, p_api_secret_key)
        if self.check_client_build_ok():
            self.client = self.client_builded[1]

    """""""""""""""""""""
    UTILITY
    """""""""""""""""""""
    # Build Client
    def build_client(self, p_api_pub_key = None, p_api_secret_key = None):
        
        # Prepare
        _inputs         = f"{self.request_timeout}|{'API_PUB_KEY_SETTED' if p_api_pub_key else None}|{'API_SECRET_KEY_SETTED' if p_api_secret_key else None} "
        _response_tuple = None        
        _temp           = None

        # Instance Binance Client
        try:
            if p_api_pub_key and p_api_secret_key:
                _temp = Client( api_key = p_api_pub_key, api_secret = p_api_secret_key, requests_params = { "timeout" : self.request_timeout } )
            else:
                _temp = Client( requests_params = { "timeout" : self.request_timeout } )
            _response_tuple = ('OK', _temp)
        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','build_client',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)
    
    # Check if the client build was successful
    def check_client_build_ok(self):
        if self.client_builded[0] == 'OK':
            return True
        else:
            return False

    # Return error when the client build went wrong 
    def get_client_msg_nok(self):
        return self.client_builded[1]

    # Truncate Asset Qta (p_qta_start) to the largest multiple of p_step_size for LOT_SIZE
    def truncate_by_step_size(self, p_qta_start, p_step_size):

        # Prepare
        _inputs             = f"{p_qta_start}|{p_step_size}"
        _response_tuple     = None        
        _digits_int         = None
        _qta_start_decimal  = None
        _qta_end            = None
        
        # By default rounding setting in python is ROUND_HALF_EVEN
        getcontext().rounding = ROUND_DOWN

        # Convert p_qta_start into Decimal
        try:
            _qta_start_decimal = Decimal(p_qta_start)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','truncate_by_step_size',_inputs,traceback.format_exc(2))}")
            return(_response_tuple)

        # Calculate Digits 4 Round
        try:
            _digits_int = int( round( -math.log(Decimal(p_step_size), 10) , 0 ) )
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','truncate_by_step_size',_inputs,traceback.format_exc(2))}")
            return(_response_tuple)

        # Calculate Tot End
        try:
            _qta_end = Decimal(round( _qta_start_decimal , _digits_int ))
            _response_tuple = ('OK',_qta_end)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','truncate_by_step_size',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)

    """""""""""""""""""""
    GENERAL ENDPOINTS
    """""""""""""""""""""
    # Check if Symbol Exists
    def general_check_if_symbol_exists(self, p_symbol_input = None):

        # Prepare
        _inputs         = None        
        _response_tuple = None
        _symbol_info    = None
        _symbol_work    = None
        
        # Choose Symbol
        if not p_symbol_input:
            _symbol_work = self.symbol
        else:
            _symbol_work = p_symbol_input

        # Set Inputs
        _inputs = f"{_symbol_work}"

        # Work
        try:
            # Check
            _symbol_info = self.client.get_symbol_info(symbol=_symbol_work)
            if _symbol_info:
                _response_tuple = ('OK', f"Symbol {_symbol_work} exist")
            else:
                _response_tuple = ('NOK', f"Symbol {_symbol_work} does not exist")
        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','general_check_if_symbol_exists',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)

    # Get Binance Rate Limits
    def general_get_rate_limits(self):

        # Prepare
        _inputs         = None
        _response_tuple = None                
        _rate_limits    = None
        _exchange_info  = None
        _output_verbose = {}

        try:

            # Get Exchange Info
            _exchange_info = self.client.get_exchange_info()
            if _exchange_info:
                _rate_limits = _exchange_info.get('rateLimits')
                if len(_rate_limits) > 0:

                    for _rate_limit in _rate_limits:

                        if _rate_limit.get('rateLimitType') == 'REQUEST_WEIGHT':

                            _key                    = f"Max Requests for {_rate_limit.get('intervalNum')} {_rate_limit.get('interval').lower().capitalize()}"
                            _output_verbose[_key]   = _rate_limit.get('limit')

                        elif _rate_limit.get('rateLimitType') == 'ORDERS' and _rate_limit.get('interval') == 'SECOND':

                            _key                    = f"Max Orders for {_rate_limit.get('intervalNum')} {_rate_limit.get('interval').lower().capitalize()}"
                            _output_verbose[_key]   = _rate_limit.get('limit')

                        elif _rate_limit.get('rateLimitType') == 'ORDERS' and _rate_limit.get('interval')== 'DAY':

                            _key                    = f"Max Orders for {_rate_limit.get('intervalNum')} {_rate_limit.get('interval').lower().capitalize()}"
                            _output_verbose[_key]   = _rate_limit.get('limit')

                        _response_tuple = ('OK', _output_verbose)

                else:
                    _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_rate_limits',_inputs,'_rate_limits is None')}")

            else:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_rate_limits',_inputs,'_exchange_info is None')}")

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','general_get_rate_limits',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)

    # Get system status detail
    def general_get_system_status(self):

        # Prepare
        _inputs         = None
        _response_tuple = None                
        _status         = None
        _output         = None

        try:
            _output = self.client.get_system_status()
            if _output:
                if not _output.get('status'):
                    _status = 'System Normal'
                else:
                    _status = 'System Maintenance'
                _response_tuple = ('OK', _status)
            else:
                _response_tuple = ('OK', 'System Maintenance')
        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','general_get_system_status',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)

    # PRICE_FILTER
    # PERCENT_PRICE
    # LOT_SIZE      --> It is used for both buy and sell
    # MIN_NOTIONAL  --> It is used for both buy and sell and it is applied on the symbol_second in the following way: quantity symbol_first * avg price symbol > minNotional of symbol
    # ICEBERG_PARTS
    # MARKET_LOT_SIZE
    # MAX_NUM_ALGO_ORDERS    
    # MAX_NUM_ORDERS
    def general_get_symbol_info_filter(self, p_what_filter, p_symbol_input = None):

        """ PREPARE """
        
        # Defaults
        _inputs                 = None
        _response_tuple         = None        
        _symbol_info            = None
        _symbol_info_dict       = {} 
        _symbol_work            = None
        _filters                = None
        _filter                 = None        
        _response_tuple_local   = None
        _output_local           = {}

        # Choose Symbol
        if not p_symbol_input:
            _symbol_work = self.symbol
        else:
            _symbol_work = p_symbol_input

        # Set Inputs
        _inputs = f"{p_what_filter}|{_symbol_work}|{self.wallet}"

        """ FUNCTIONS FOR EVERY FILTER """

        # Get PRICE_FILTER info
        def price_filter(_symbol, _filter):
            try:
                if self.wallet == 'spot' or self.wallet == 'margin' or self.wallet == 'futures':
                    _output_local["PRICE_FILTER_symbol"]     = _symbol
                    _output_local["PRICE_FILTER_minPrice"]   = Decimal(_filter.get('minPrice')) if _filter.get('minPrice') else _filter.get('minPrice')
                    _output_local["PRICE_FILTER_maxPrice"]   = Decimal(_filter.get('maxPrice')) if _filter.get('maxPrice') else _filter.get('maxPrice')
                    _output_local["PRICE_FILTER_tickSize"]   = Decimal(_filter.get('tickSize')) if _filter.get('tickSize') else _filter.get('tickSize')
                    _response_tuple_local = ('OK', _output_local)
                else:
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.price_filter',_inputs,self.wallet+': wallet is unknown')}")
            except Exception:
                _response_tuple_local = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_info_filter.price_filter',_inputs,traceback.format_exc(2))}")
            return(_response_tuple_local)

        # Get PERCENT_PRICE info
        def percent_price(_symbol, _filter):
            try:
                if self.wallet == 'spot' or self.wallet == 'margin' or self.wallet == 'futures':
                    _output_local["PERCENT_PRICE_symbol"] = _symbol                    
                    if self.wallet == 'spot' or self.wallet == 'margin':
                        _output_local["PERCENT_PRICE_avgPriceMins"] = int(_filter.get('avgPriceMins')) if _filter.get('avgPriceMins') else _filter.get('avgPriceMins')                                
                    else:
                        _output_local["PERCENT_PRICE_multiplierDecimal"] = int(_filter.get('multiplierDecimal')) if _filter.get('multiplierDecimal') else _filter.get('multiplierDecimal')                                
                    _output_local["PERCENT_PRICE_multiplierUp"]     = Decimal(_filter.get('multiplierUp'))      if _filter.get('multiplierUp')      else _filter.get('multiplierUp')
                    _output_local["PERCENT_PRICE_multiplierDown"]   = Decimal(_filter.get('multiplierDown'))    if _filter.get('multiplierDown')    else _filter.get('multiplierDown')
                    _response_tuple_local = ('OK', _output_local)
                else:
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.percent_price',_inputs,self.wallet+': wallet is unknown')}")                    
            except Exception:
                _response_tuple_local = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_info_filter.percent_price',_inputs,traceback.format_exc(2))}")
            return(_response_tuple_local)
        
        # Get LOT_SIZE info
        def lot_size(_symbol, _filter):
            try:
                if self.wallet == 'spot' or self.wallet == 'margin' or self.wallet == 'futures':                
                    _output_local["LOT_SIZE_symbol"]     = _symbol
                    _output_local["LOT_SIZE_maxQty"]     = Decimal(_filter.get('maxQty'))    if _filter.get('maxQty')    else _filter.get('maxQty')
                    _output_local["LOT_SIZE_minQty"]     = Decimal(_filter.get('minQty'))    if _filter.get('minQty')    else _filter.get('minQty') # quantity to buy or sell > symbol minQty
                    _output_local["LOT_SIZE_stepSize"]   = Decimal(_filter.get('stepSize'))  if _filter.get('stepSize')  else _filter.get('stepSize') # the quantity to buy or sell must be an exact multiple of symbol stepSize
                    _response_tuple_local = ('OK', _output_local)
                else:
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.lot_size',_inputs,self.wallet+': wallet is unknown')}")                                
            except Exception:
                _response_tuple_local = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_info_filter.lot_size',_inputs,traceback.format_exc(2))}")
            return(_response_tuple_local)

        # Get MIN_NOTIONAL info
        def min_notional(_symbol, _filter):
            try:
                if self.wallet == 'spot' or self.wallet == 'margin':                    
                    _output_local["MIN_NOTIONAL_symbol"]         = _symbol
                    _output_local["MIN_NOTIONAL_minNotional"]    = Decimal(_filter.get('minNotional')) if _filter.get('minNotional') else _filter.get('minNotional')
                    _output_local["MIN_NOTIONAL_applyToMarket"]  = _filter.get('applyToMarket')
                    _output_local["MIN_NOTIONAL_avgPriceMins"]   = int(_filter.get('avgPriceMins')) if _filter.get('avgPriceMins') else _filter.get('avgPriceMins')
                    _response_tuple_local = ('OK', _output_local)
                elif self.wallet == 'futures':
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.min_notional',_inputs,self.wallet+': attention! for this wallet min_notional does not exist ')}")                                
                else:
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.min_notional',_inputs,self.wallet+': wallet is unknown')}")               
            except Exception:
                _response_tuple_local = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_info_filter.min_notional',_inputs,traceback.format_exc(2))}")
            return(_response_tuple_local)

        # Get ICEBERG_PARTS info
        def iceberg_parts(_symbol, _filter):
            try:
                if self.wallet == 'spot' or self.wallet == 'margin':                    
                    _output_local["ICEBERG_PARTS_symbol"]   = _symbol
                    _output_local["ICEBERG_PARTS_limit"]    = int(_filter.get('limit')) if _filter.get('limit') else _filter.get('limit')
                    _response_tuple_local = ('OK', _output_local)
                elif self.wallet == 'futures':
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.iceberg_parts',_inputs,self.wallet+': attention! for this wallet iceberg_parts does not exist ')}")                                
                else:
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.iceberg_parts',_inputs,self.wallet+': wallet is unknown')}")               
            except Exception:
                _response_tuple_local = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_info_filter.iceberg_parts',_inputs,traceback.format_exc(2))}")
            return(_response_tuple_local)

        # Get MARKET_LOT_SIZE info
        def market_lot_size(_symbol, _filter):
            try:
                if self.wallet == 'spot' or self.wallet == 'margin' or self.wallet == 'futures':                
                    _output_local["MARKET_LOT_SIZE_symbol"]      = _symbol
                    _output_local["MARKET_LOT_SIZE_minQty"]      = Decimal(_filter.get('minQty'))    if _filter.get('minQty')    else _filter.get('minQty')
                    _output_local["MARKET_LOT_SIZE_maxQty"]      = Decimal(_filter.get('maxQty'))    if _filter.get('maxQty')    else _filter.get('maxQty')
                    _output_local["MARKET_LOT_SIZE_stepSize"]    = Decimal(_filter.get('stepSize'))  if _filter.get('stepSize')  else _filter.get('stepSize')
                    _response_tuple_local = ('OK', _output_local)
                else:
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.market_lot_size',_inputs,self.wallet+': wallet is unknown')}")                    
            except Exception:
                _response_tuple_local = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_info_filter.market_lot_size',_inputs,traceback.format_exc(2))}")
            return(_response_tuple_local)

        # Get MAX_NUM_ALGO_ORDERS info
        def max_num_algo_orders(_symbol, _filter):
            try:
                if self.wallet == 'spot' or self.wallet == 'margin' or self.wallet == 'futures':
                    _output_local["MAX_NUM_ALGO_ORDERS_symbol"] = _symbol
                    if self.wallet == 'spot' or self.wallet == 'margin':
                        _output_local["MAX_NUM_ALGO_ORDERS_maxNumAlgoOrders"] = int(_filter.get('maxNumAlgoOrders')) if _filter.get('maxNumAlgoOrders') else _filter.get('maxNumAlgoOrders')                                
                    else:
                        _output_local["MAX_NUM_ALGO_ORDERS_limit"] = int(_filter.get('limit')) if _filter.get('limit') else _filter.get('limit')
                    _response_tuple_local = ('OK', _output_local)                                                        
                else:
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.max_num_algo_orders',_inputs,self.wallet+': wallet is unknown')}")                    
            except Exception:
                _response_tuple_local = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_info_filter.max_num_algo_orders',_inputs,traceback.format_exc(2))}")
            return(_response_tuple_local)

        # Get MAX_NUM_ORDERS info
        def max_num_orders(_symbol, _filter):
            try:
                if self.wallet == 'spot' or self.wallet == 'margin' or self.wallet == 'futures':
                    _output_local["MAX_NUM_ORDERS_symbol"] = _symbol
                    if self.wallet == 'spot' or self.wallet == 'margin':
                        _output_local["MAX_NUM_ORDERS_maxNumOrders"] = int(_filter.get('maxNumOrders')) if _filter.get('maxNumOrders') else _filter.get('maxNumOrders')                                
                    else:
                        _output_local["MAX_NUM_ORDERS_limit"] = int(_filter.get('limit')) if _filter.get('limit') else _filter.get('limit') 
                    _response_tuple_local = ('OK', _output_local)                                                       
                else:
                    _response_tuple_local = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter.max_num_orders',_inputs,self.wallet+': wallet is unknown')}")                    
            except Exception:
                _response_tuple_local = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_info_filter.max_num_orders',_inputs,traceback.format_exc(2))}")
            return(_response_tuple_local)

        """ GET SYMBOL INFO """
        try:
            if self.wallet == 'spot' or self.wallet == 'margin':
                _symbol_info = self.client.get_symbol_info(symbol=_symbol_work)
            elif self.wallet == 'futures':
                _symbol_info_dict = self.client.futures_exchange_info()                 
                if _symbol_info_dict['symbols']:                    
                    for f in _symbol_info_dict['symbols']:
                        if f.get('symbol') == _symbol_work:
                            _symbol_info = f                           
                            break
                else:
                    _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter',_inputs,_symbol_info_dict['symbols']+': _symbol_info_dict[symbols] is None')}")
                    return(_response_tuple)   
            else:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter',_inputs,self.wallet+': wallet is unknown')}")
                return(_response_tuple)
        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
            return(_response_tuple)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_info_filter',_inputs,traceback.format_exc(2))}")
            return(_response_tuple)

        """ WORK ON SYMBOL INFO """
        if _symbol_info:
            _filters = _symbol_info.get('filters')
            if len(_filters) > 0:
                for _filter in _filters:
                                        
                    if _filter.get('filterType') == p_what_filter:

                        if p_what_filter == 'PRICE_FILTER':
                            _response_tuple = price_filter(_symbol_work, _filter)
                            break
                        elif p_what_filter == 'PERCENT_PRICE':
                            _response_tuple = percent_price(_symbol_work, _filter)
                            break
                        elif p_what_filter == 'LOT_SIZE':
                            _response_tuple = lot_size(_symbol_work, _filter)
                            break
                        elif p_what_filter == 'MIN_NOTIONAL':                            
                            _response_tuple = min_notional(_symbol_work, _filter)
                            break
                        elif p_what_filter == 'ICEBERG_PARTS':
                            _response_tuple = iceberg_parts(_symbol_work, _filter)
                            break
                        elif p_what_filter == 'MARKET_LOT_SIZE':
                            _response_tuple = market_lot_size(_symbol_work, _filter)
                            break
                        elif p_what_filter == 'MAX_NUM_ALGO_ORDERS':
                            _response_tuple = max_num_algo_orders(_symbol_work, _filter)
                            break                            
                        elif p_what_filter == 'MAX_NUM_ORDERS':
                            _response_tuple = max_num_orders(_symbol_work, _filter)
                            break
                        else:                          
                            _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter',_inputs,p_what_filter+': what_filter is unknown')}")

                    else:                          
                        _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter',_inputs,p_what_filter+': what_filter is unknown')}")
            else:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter',_inputs,'_filters is None')}")

        else:
            _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_info_filter',_inputs,'_symbol_info is None')}")

        return(_response_tuple)

    # Get Symbol Fee Cost
    # https://binance.zendesk.com/hc/en-us/articles/360007720071-Maker-vs-Taker
    def general_get_symbol_fee_cost(self, p_what_fee='taker', p_symbol_input = None):

        # Prepare
        _inputs             = None 
        _response_tuple     = None               
        _fee_decimal        = None
        _trade_fee_response = None
        _symbol_exists      = None
        _trade_fee          = {}
        _symbol_work        = None

        # Choose Symbol
        if not p_symbol_input:
            _symbol_work = self.symbol
        else:
            _symbol_work = p_symbol_input

        # Set Inputs
        _inputs = f"{_symbol_work}|{p_what_fee}"

        # Check if Symbol Exists
        _symbol_exists  = self.general_check_if_symbol_exists(_symbol_work)
        if _symbol_exists[0] == 'NOK':
            _response_tuple = (_symbol_exists[0], _symbol_exists[1])
            return(_response_tuple)

        try:
            # Get Trade Fee Response
            _trade_fee_response = self.client.get_trade_fee(symbol=_symbol_work)

            # Work on Trade Fee Response
            if _trade_fee_response:
                if (_trade_fee_response.get('success')):
                    _trade_fee = _trade_fee_response.get('tradeFee')
                    if len(_trade_fee) > 0: # Checking if dictionary _trade_fee is empty
                        for t in _trade_fee:
                            if t.get('symbol') == _symbol_work:
                                try:
                                    _fee_decimal = Decimal(t.get(p_what_fee))
                                    _response_tuple = ('OK', _fee_decimal)
                                except Exception:
                                    _response_tuple = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_fee_cost',_inputs,traceback.format_exc(2))}")
                                    return(_response_tuple)
                    else:
                        _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_fee_cost',_inputs,'_trade_fee is Empty')}")
                else:
                    _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_fee_cost',_inputs,'get_trade_fee() insuccess')}")
            else:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_fee_cost',_inputs,'_trade_fee_response is None')}")

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_fee_cost',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)

    # Get Average price in the last 5 minutes
    def general_get_symbol_avg_price(self, p_symbol_input = None):

        # Prepare
        _inputs             = None 
        _response_tuple     = None                  
        _price_decimal      = None
        _avg_price_response = None
        _symbol_exists      = None
        _symbol_work        = None

        # Choose Symbol
        if not p_symbol_input:
            _symbol_work = self.symbol
        else:
            _symbol_work = p_symbol_input

        # Set Inputs
        _inputs = f"{_symbol_work}"

        # Check if Symbol Exists
        _symbol_exists = self.general_check_if_symbol_exists(_symbol_work)
        if _symbol_exists[0] == 'NOK':
            _response_tuple = (_symbol_exists[0],  _symbol_exists[1])
            return(_response_tuple)

        # Get Avg Price
        try:

            _avg_price_response = self.client.get_avg_price(symbol=_symbol_work)
            if _avg_price_response:
                _price_decimal = Decimal(_avg_price_response.get('price'))
                _response_tuple = ('OK', _price_decimal)
            else:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_avg_price',_inputs,'_avg_price_response is None')}")

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_avg_price',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)

    # Get Mark Price - only Futures
    def general_get_symbol_mark_price(self, p_symbol_input = None):

        # Prepare
        _inputs                 = None 
        _response_tuple         = None                  
        _mark_price_decimal     = None
        _response               = None
        _symbol_exists          = None
        _symbol_work            = None

        # Choose Symbol
        if not p_symbol_input:
            _symbol_work = self.symbol
        else:
            _symbol_work = p_symbol_input

        # Set Inputs
        _inputs = f"{_symbol_work}"

        # Check if Symbol Exists
        _symbol_exists = self.general_check_if_symbol_exists(_symbol_work)
        if _symbol_exists[0] == 'NOK':
            _response_tuple = (_symbol_exists[0],  _symbol_exists[1])
            return(_response_tuple)

        # Get Avg Price
        try:

            _response = self.client.futures_mark_price(symbol=_symbol_work)
            if _response:
                _mark_price_decimal = Decimal(_response.get('markPrice'))
                _response_tuple = ('OK', _mark_price_decimal)
            else:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','general_get_symbol_mark_price',_inputs,'_response is None')}")

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','general_get_symbol_mark_price',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)


    """""""""""""""""""""""""""""""""""""""""""""
    ACCOUNT ENDPOINTS (SPOT + MARGIN + FUTURES)
    """""""""""""""""""""""""""""""""""""""""""""

    """ GENERIC """

    # Get Account Balance Total (free & locked) --> spot + margin
    def account_get_balance_total(self):

        # Prepare
        _inputs             = f"{self.wallet}"
        _response_tuple     = None                
        _my_balance         = []
        _my_asset           = {}
        _account_info       = None
        _what_find          = None
        _what_finds         = None   

        _symbol_temp_btc        = None
        _symbol_temp_usdt       = None
        _avg_price_temp_btc     = 0
        _avg_price_temp_usdt    = 0

        _tot_btc_free       = 0
        _tot_btc_locked     = 0
        _tot_usd_free       = 0
        _tot_usd_locked     = 0
        _tot_btc            = 0
        _tot_usd            = 0

        try:
                                    
            # Get Account Info
            if self.wallet == 'spot':
                _account_info   = self.client.get_account()
                _what_finds     = "balances"
            elif self.wallet == 'margin':
                _account_info   = self.client.get_margin_account()
                _what_finds     = "userAssets"
            elif self.wallet == 'futures':
                _what_finds     = 'no_what_finds'
                _account_info   = self.client.futures_account_balance()
        
        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_balance_total',_inputs,traceback.format_exc(2))}") 
                
        # Get Values from Account Info
        if _what_finds in _account_info:
            
            # For every Balances
            for _what_find in _account_info[_what_finds]:

                if ( Decimal(_what_find.get('free')) + Decimal(_what_find.get('locked')) ) > 0: # Only Asset with something

                    """""""""""""""""""""""""""""""""
                     Build Wallet with List Assets Dict
                    """""""""""""""""""""""""""""""""
                    # Build Asset Dict
                    _my_asset = {   'asset'     : _what_find.get('asset'),
                                    'free'      : Decimal(_what_find.get('free')),
                                    'locked'    : Decimal(_what_find.get('locked'))    }

                    # Build List Assets Dict
                    _my_balance.append(_my_asset)

                    """""""""""""""""""""""""""""""""
                    Build Estimated TOT Value BTC & USD
                    """""""""""""""""""""""""""""""""
                    # Asset BTC
                    if _my_asset.get('asset') == 'BTC':

                        # Tot Btc
                        _tot_btc_free   = _tot_btc_free + _my_asset.get('free')
                        _tot_btc_locked = _tot_btc_locked + _my_asset.get('locked')
                        
                        # Tot Usd
                        _avg_price_temp = self.general_get_symbol_avg_price('BTCUSDT')
                        if _avg_price_temp[0] == 'OK':
                            _tot_usd_free   = _tot_usd_free + (_avg_price_temp[1] * _my_asset.get('free'))
                            _tot_usd_locked = _tot_usd_locked + (_avg_price_temp[1] * _my_asset.get('locked'))
                            _response_tuple = ('OK',  True)
                        else:
                            _response_tuple = ('NOK',  _avg_price_temp[1])
                    
                    # Asset USDT
                    elif _my_asset.get('asset') == 'USDT':
                        
                        # Tot Btc
                        _avg_price_temp = self.general_get_symbol_avg_price('BTCUSDT')
                        if _avg_price_temp[0] == 'OK':
                            _tot_btc_free   = _tot_btc_free + (_my_asset.get('free') / _avg_price_temp[1])
                            _tot_btc_locked = _tot_btc_locked + (_my_asset.get('locked') / _avg_price_temp[1])
                            _response_tuple = ('OK',  True)                            
                        else:
                            _response_tuple = ('NOK', _avg_price_temp[1])
                        
                        # Tot Usd
                        _tot_usd_free      = _tot_usd_free + _my_asset.get('free')
                        _tot_usd_locked    = _tot_usd_locked + _my_asset.get('locked')                                

                    # Asset BUSD
                    elif _my_asset.get('asset') == 'BUSD':

                        # Tot Btc
                        _avg_price_temp = self.general_get_symbol_avg_price('BTCBUSD')
                        if _avg_price_temp[0] == 'OK':
                            _tot_btc_free   = _tot_btc_free + (_my_asset.get('free') / _avg_price_temp[1])
                            _tot_btc_locked = _tot_btc_locked + (_my_asset.get('locked') / _avg_price_temp[1])
                            _response_tuple = ('OK',  True)                            
                        else:
                            _response_tuple = ('NOK', _avg_price_temp[1])
                        
                        # Tot Usd
                        _tot_usd_free      = _tot_usd_free + _my_asset.get('free')
                        _tot_usd_locked    = _tot_usd_locked + _my_asset.get('locked')

                    # Asset ALTCOIN
                    else:

                        # Prepare 4 Tot Btc & Tot Usd
                        _symbol_temp_btc    = f"{_my_asset.get('asset')}BTC"
                        _symbol_temp_usdt   = f"{_my_asset.get('asset')}USDT"

                        # Tot Btc
                        _avg_price_temp_btc = self.general_get_symbol_avg_price(_symbol_temp_btc)
                        if _avg_price_temp_btc[0] == 'OK':
                            _tot_btc_free   = _tot_btc_free + (_avg_price_temp_btc[1] * _my_asset.get('free'))
                            _tot_btc_locked = _tot_btc_locked + (_avg_price_temp_btc[1] * _my_asset.get('locked'))                            
                        """ 
                        TOLTO perchè potrebbe dare 'Symbol LDsymbol_firstUSDT does not exist'
                        Questo perchè se si mette un symbol_first su Savings gli antenpone LD, mentre se si mettono su POOL non le elenca proprio
                        Esempio: {'asset': 'LDDOT', 'free': '253.08828200',  'locked': '0.00000000'}
                        
                        else:
                            _response_tuple = ('NOK', _avg_price_temp_btc[1])
                        """
                        
                        # Tot Usd    
                        _avg_price_temp_usdt = self.general_get_symbol_avg_price(_symbol_temp_usdt)
                        if _avg_price_temp_usdt[0] == 'OK':
                            _tot_usd_free   = _tot_usd_free + (_avg_price_temp_usdt[1] * _my_asset.get('free'))
                            _tot_usd_locked = _tot_usd_locked + (_avg_price_temp_usdt[1] * _my_asset.get('locked'))
                        """
                        TOLTO perchè potrebbe dare 'Symbol LDsymbol_firstUSDT does not exist'
                        Questo perchè se si mette un symbol_first su Savings gli antenpone LD, mentre se si mettono su POOL non le elenca proprio
                        Esempio: {'asset': 'LDDOT', 'free': '253.08828200',  'locked': '0.00000000'}
                                                
                        else:
                            _response_tuple = ('NOK',  _avg_price_temp_usdt[1])
                        """
                        
                        _response_tuple = ('OK',  True)
                                
            if _response_tuple[0] == 'OK':
                
                 # Add Estimated Value BTC & USD at the first position of the list
                _tot_btc = _tot_btc_free + _tot_btc_locked
                _tot_usd = _tot_usd_free + _tot_usd_locked

                _my_balance.insert( 0 , { 'totals' : {  'tot_btc_free': _tot_btc_free,
                                                        'tot_btc_locked': _tot_btc_locked,
                                                        'tot_usd_free': _tot_usd_free,
                                                        'tot_usd_locked': _tot_usd_locked,
                                                        'tot_btc': _tot_btc,
                                                        'tot_usd': _tot_usd   }   }   )

                _response_tuple = ('OK', _my_balance)

        else:
            
            # Furues Wallet
            if self.wallet == 'futures' and _account_info:
                
                # For every Asset
                for _what_find in _account_info:
                    
                     if ( Decimal(_what_find.get('balance')) ) > 0: # Only Asset with something
                         
                        """""""""""""""""""""""""""""""""
                        Build Wallet with List Assets Dict
                        """""""""""""""""""""""""""""""""
                        # Build Asset Dict
                        _my_asset = {   'asset'     : _what_find.get('asset'),
                                        'free'      : Decimal(_what_find.get('withdrawAvailable')),
                                        'locked'    : Decimal(_what_find.get('balance')) - Decimal(_what_find.get('withdrawAvailable'))   }

                        # Build List Assets Dict
                        _my_balance.append(_my_asset)
                        
                        if _my_asset.get('asset') == 'USDT':
                            _tot_usd = _tot_usd + Decimal(_what_find.get('balance'))
                
                # Add Total USD at the first position of the list
                _my_balance.insert( 0 , { 'totals' : { 'tot_usd': _tot_usd }   }   )
                
                # Result
                _response_tuple = ('OK', _my_balance)
                
            else:
                
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_balance_total',_inputs,_what_finds+' not in _account_info')}")

        return(_response_tuple)

    # Get Account Balance Asset Free  --> spot + margin + futures
    def account_get_balance_asset_free(self, p_symbol):

        # Prepare 
        _inputs                     = f"{self.wallet}|{p_symbol}"
        _response_tuple             = None                
        _asset_balance_response     = None
        _assets_balance_response    = None
        _bal_decimal                = None

        try:

            if self.wallet == 'spot':

                _asset_balance_response = self.client.get_asset_balance(asset=p_symbol)
                if _asset_balance_response:
                    if _asset_balance_response.get('free'):
                        _bal_decimal = Decimal(_asset_balance_response.get('free'))
                        _response_tuple = ('OK', _bal_decimal)
                    else:
                        _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_balance_asset_free',_inputs,'_asset_balance_response.get(free) is None')}")
                else:
                    _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_balance_asset_free',_inputs,'_asset_balance_response is None')}")

            elif self.wallet == 'margin':

                _account_info   = None
                _what_find      = None
                _what_finds     = "userAssets"

                _account_info = self.client.get_margin_account()
                if _what_finds in _account_info:

                    for _what_find in _account_info[_what_finds]: # For every Balances

                        if _what_find.get('asset') == p_symbol.upper():
                            _bal_decimal = Decimal(_what_find.get('free'))
                            _response_tuple = ('OK',  _bal_decimal)
                            break
                        else:
                            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_balance_asset_free',_inputs,p_symbol+' not found')}")
                            continue

            elif self.wallet == 'futures':

                _assets_balance_response = self.account_get_balance_total()
                if _assets_balance_response[0] == 'OK':
                    for _asset_balance_response in _assets_balance_response[1]:
                        if _asset_balance_response.get('asset') == p_symbol.upper(): 
                            if _asset_balance_response.get('free'):
                                _bal_decimal = Decimal(_asset_balance_response.get('free'))
                                _response_tuple = ('OK', _bal_decimal)
                                break
                            else:
                                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_balance_asset_free',_inputs,'_asset_balance_response.get(free) is None')}")
                        else:
                            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_balance_asset_free',_inputs, p_symbol.upper()+' not found')}")
                else:
                    _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_balance_asset_free',_inputs,_assets_balance_response[1])}")

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_balance_asset_free',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)

    # Calculate Account exact Quantity to BUY --> spot + margin
    def account_get_quantity_to_buy(self, p_what_fee, p_type, p_size, p_how2get_qta2buy, p_price = None):

        # Prepare
        _inputs                             = f"{self.wallet}|{p_what_fee}|{p_type}|{p_size}|{p_how2get_qta2buy}|{p_price}|{self.symbol_first}|{self.symbol_second}"
        _response_tuple                     = None
        _symbol_bal_second_free             = None
        _symbol_bal_second_tot_estimated    = None
        _symbol_lot_size                    = None        
        _symbol_step_size_value             = None
        _symbol_min_qty_value               = None
        _symbol_min_notional                = None
        _symbol_min_notional_value          = None
        _symbol_price                       = None
        _symbol_price_value                 = None
        _symbol_fee                         = None 
        _symbol_fee_value                   = None                        
        _symbol_fee_perc                    = None

        # Prepare Quantity Vars
        quantity_pre_size_applied       = None
        quantity_post_size_applied      = None
        quantity_pre_stepSize_applied   = None
        quantity_post_stepSize_applied  = None
        quantity_processed_final        = None

        # By default rounding setting in python is ROUND_HALF_EVEN
        getcontext().rounding = ROUND_DOWN

        """ Get Owned Second Asset Balance Free """
        _symbol_bal_second_free = self.account_get_balance_asset_free(self.symbol_second)
        if _symbol_bal_second_free[0] != 'OK':        
            _response_tuple = ('NOK', _symbol_bal_second_free[1])
            return(_response_tuple)
                
        """ Get Owned Second Asset Balance """
        if p_how2get_qta2buy == 'total':

            # Symbol Bal Second TOT Estimated Asset Balance
            _symbol_bal_second_tot_estimated = self.account_get_balance_total()
            if _symbol_bal_second_tot_estimated[0] == 'OK':
                pass
                # DA RIVEVEDERE PERCHÈ CON SELF.SYMBOL_SECOND = USDT NON FUNZIONEREBBE
                #quantity_pre_size_applied = _symbol_bal_second_tot_estimated[1][0].get('totals').get(f"tot_{self.symbol_second.lower()}")                
            else:
                _response_tuple = ('NOK', _symbol_bal_second_tot_estimated[1])
                return(_response_tuple)

        elif p_how2get_qta2buy == 'only_available':

            # Symbol Bal Second AVAILABLE Asset Balance
            quantity_pre_size_applied = _symbol_bal_second_free[1]

        """ Build bal to use & size """
        # I break down the formula quantity_post_size_applied = round(Decimal(quantity_pre_size_applied) / Decimal(100) *  Decimal(p_size), 5)
        # into elementary steps

        # Default Value
        _p_size_str = None
        _p_size_decimal = None
        _quantity_pre_size_applied_decimal = None
        _100_int = 100
        _100_str = None
        _100_decimal = None
        _division = None
        _multiplication = None        
        _inputs_temp = None
        
        # Prepare p_size ( str -> decimal )
        _p_size_str = str(p_size)
        try:
            _p_size_decimal = Decimal(_p_size_str)
        except Exception:
            _inputs_temp = f"||{type(p_size)},{p_size}|{type(_p_size_str)},{_p_size_str}|{type(_p_size_decimal)},{_p_size_decimal}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_buy',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)

        # Prepare 100 ( str -> decimal )
        _100_str = str(_100_int)
        try:
            _100_decimal = Decimal(_100_str)
        except Exception:
            _inputs_temp = f"||{type(_100_int)},{_100_int}|{type(_100_str)},{_100_str}|{type(_100_decimal)},{_100_decimal}"            
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_buy',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)

        # Prepare quantity_pre_size_applied
        try:            
            _quantity_pre_size_applied_decimal = Decimal(quantity_pre_size_applied)
        except Exception:
            _inputs_temp = f"||{type(quantity_pre_size_applied)},{quantity_pre_size_applied}|{type(_quantity_pre_size_applied_decimal)},{_quantity_pre_size_applied_decimal}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_buy',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)

        # Operate Division
        try:
            _division = _quantity_pre_size_applied_decimal / _100_decimal
        except Exception:
            _inputs_temp = f"||{type(_100_decimal)},{_100_decimal}|{type(_quantity_pre_size_applied_decimal)},{_quantity_pre_size_applied_decimal}|{type(_division)},{_division}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_buy',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)
        
        # Operate Multiplication
        try:                 
            _multiplication = _division * _p_size_decimal
        except Exception:
            _inputs_temp = f"||{type(_p_size_decimal)},{_p_size_decimal}|{type(_division)},{_division}|{type(_multiplication)},{_multiplication}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_buy',_inputs,traceback.format_exc(2))}")
            return(_response_tuple)
        
        # Operate Round
        try:             
            quantity_post_size_applied = round(_multiplication, 5)
        except Exception:
            _inputs_temp = f"||{type(_multiplication)},{_multiplication}|{type(quantity_post_size_applied)},{quantity_post_size_applied}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_buy',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)

        # Stop Qta to BUY TO Real Free Qta
        try:               
            if quantity_post_size_applied > _symbol_bal_second_free[1]:
                quantity_post_size_applied = _symbol_bal_second_free[1]
        except Exception:
            _inputs_temp = f"||{type(_symbol_bal_second_free[1])},{_symbol_bal_second_free[1]}|{type(quantity_post_size_applied)},{quantity_post_size_applied}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_buy',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)
                                                

        """ Get Symbol Filter LOT_SIZE """
        _symbol_lot_size = self.general_get_symbol_info_filter('LOT_SIZE')
        if _symbol_lot_size[0] != 'OK':
            _response_tuple = ('NOK',  _symbol_lot_size[1])
            return(_response_tuple)                    

        """ Get Symbol Filter MIN_NOTIONAL """
        _symbol_min_notional = self.general_get_symbol_info_filter('MIN_NOTIONAL')
        if _symbol_min_notional[0] != 'OK':
            _response_tuple = ('NOK', _symbol_min_notional[1])
            return(_response_tuple)

        """ Get Symbol Fee Cost """
        _symbol_fee = self.general_get_symbol_fee_cost(p_what_fee)
        if _symbol_fee[0] != 'OK':
            _response_tuple = ('NOK',  _symbol_fee[1])
            return(_response_tuple)

        """ Get Symbol Avg Price or Symbol Input Price """
        if p_type == 'market':
            _symbol_price = self.general_get_symbol_avg_price() # Avg Price
            if _symbol_price[0] != 'OK':
                _response_tuple = ('NOK',  _symbol_price[1])
                return(_response_tuple)
        elif (p_type == 'limit' or p_type == 'stop_limit' or p_type == 'oco') and p_price:
            try:
                _symbol_price = tuple( ( 'OK' , Decimal(p_price) ) ) # Input Price
            except Exception:
                _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_buy',_inputs,traceback.format_exc(2))}")
                return(_response_tuple)

        else:
            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_quantity_to_buy',_inputs,'p_type unknown or p_price is None')}")
            return(_response_tuple)

        """ Calculate Quantity End """
        
        _symbol_min_qty_value          = _symbol_lot_size[1].get('LOT_SIZE_minQty')        
        _symbol_step_size_value        = _symbol_lot_size[1].get('LOT_SIZE_stepSize')
        _symbol_min_notional_value     = _symbol_min_notional[1].get('MIN_NOTIONAL_minNotional')
        _symbol_fee_value              = _symbol_fee[1]
        _symbol_price_value            = _symbol_price[1]
        
        # Fee % Applied
        try:
            _symbol_fee_perc                = (Decimal(100) - _symbol_fee_value) / Decimal(100)
            quantity_pre_stepSize_applied   = (quantity_post_size_applied / _symbol_price_value) * _symbol_fee_perc
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_buy',_inputs,traceback.format_exc(2))}")
            return(_response_tuple)

        # Truncate By Step Size
        quantity_post_stepSize_applied = self.truncate_by_step_size(quantity_pre_stepSize_applied, _symbol_step_size_value)
        if quantity_post_stepSize_applied[0] != 'OK':
            _msg                = quantity_post_stepSize_applied[1]
            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_quantity_to_buy',_inputs,_msg)}")
            return(_response_tuple)
        quantity_processed_final = quantity_post_stepSize_applied[1]
        
        # Output
        if quantity_processed_final > _symbol_min_qty_value:

            if (_symbol_price_value * quantity_processed_final) > _symbol_min_notional_value:

                """
                if p_size == 100:
                    quantity_processed_final = quantity_processed_final - _symbol_step_size_value # To avoid "Account has insufficient balance for requested action" if there is a pump in progress
                """

                _response_tuple = ('OK', tuple((quantity_processed_final, quantity_pre_size_applied, quantity_post_size_applied)) )

            else:
                _msg                = f"Quantity * Price (= {quantity_pre_stepSize_applied*_symbol_price_value:.10f}) to make BUY is not > Symbol Min Notional Qty (= {_symbol_min_notional_value})"
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_quantity_to_buy',_inputs,_msg)}")

        else:
            _msg                = f"Quantity (= {quantity_pre_stepSize_applied:.10f}) to make BUY is not > Symbol Min Qty (= {_symbol_min_qty_value})"
            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_quantity_to_buy',_inputs,_msg)}")

        return(_response_tuple)

    # Calculate Account exact Quantity to SELL --> spot + margin
    def account_get_quantity_to_sell(self, p_type, p_size, p_price = None):

        # Prepare
        _inputs                     = f"{self.wallet}|{p_type}|{p_size}|{p_price}|{self.symbol_first}|{self.symbol_second}"
        _response_tuple             = None        
        _symbol_step_size_value     = None
        _symbol_min_qty_value       = None
        _symbol_min_notional        = None
        _symbol_lot_size            = None
        _symbol_min_notional_value  = None        
        _symbol_price               = None
        _symbol_price_value         = None
        

        # Prepare Quantity Vars
        quantity_pre_size_applied       = None
        quantity_post_size_applied      = None
        quantity_pre_stepSize_applied   = None
        quantity_post_stepSize_applied  = None
        quantity_processed_final        = None

        """ Get Owned Asset Balance Free """
        _symbol_bal_first_free = self.account_get_balance_asset_free(self.symbol_first)
        if _symbol_bal_first_free[0] != 'OK':
            _response_tuple = ('NOK',  _symbol_bal_first_free[1])
            return(_response_tuple)

        """ Build bal to use & size """
        quantity_pre_size_applied = _symbol_bal_first_free[1]


        # I break down the formula quantity_post_size_applied = round(Decimal(quantity_pre_size_applied) / Decimal(100) *  Decimal(p_size), 5)
        # into elementary steps

        # Default Value
        _p_size_str = None
        _p_size_decimal = None
        _quantity_pre_size_applied_decimal = None
        _100_int = 100
        _100_str = None
        _100_decimal = None
        _division = None
        _multiplication = None        
        _inputs_temp = None      

        # Prepare p_size ( str -> decimal )
        _p_size_str = str(p_size)
        try:
            _p_size_decimal = Decimal(_p_size_str)
        except Exception:
            _inputs_temp = f"||{type(p_size)},{p_size}|{type(_p_size_str)},{_p_size_str}|{type(_p_size_decimal)},{_p_size_decimal}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_sell',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)

        # Prepare 100 ( str -> decimal )
        _100_str = str(_100_int)
        try:
            _100_decimal = Decimal(_100_str)
        except Exception:
            _inputs_temp = f"||{type(_100_int)},{_100_int}|{type(_100_str)},{_100_str}|{type(_100_decimal)},{_100_decimal}"            
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_sell',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)

        # Prepare quantity_pre_size_applied
        try:            
            _quantity_pre_size_applied_decimal = Decimal(quantity_pre_size_applied)
        except Exception:
            _inputs_temp = f"||{type(quantity_pre_size_applied)},{quantity_pre_size_applied}|{type(_quantity_pre_size_applied_decimal)},{_quantity_pre_size_applied_decimal}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_sell',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)

        # Operate Division
        try:
            _division = _quantity_pre_size_applied_decimal / _100_decimal
        except Exception:
            _inputs_temp = f"||{type(_100_decimal)},{_100_decimal}|{type(_quantity_pre_size_applied_decimal)},{_quantity_pre_size_applied_decimal}|{type(_division)},{_division}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_sell',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)
        
        # Operate Multiplication
        try:                 
            _multiplication = _division * _p_size_decimal
        except Exception:
            _inputs_temp = f"||{type(_p_size_decimal)},{_p_size_decimal}|{type(_division)},{_division}|{type(_multiplication)},{_multiplication}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_sell',_inputs,traceback.format_exc(2))}")
            return(_response_tuple)
        
        # Operate Round
        try:             
            quantity_post_size_applied = round(_multiplication, 5)
        except Exception:
            _inputs_temp = f"||{type(_multiplication)},{_multiplication}|{type(quantity_post_size_applied)},{quantity_post_size_applied}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_sell',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)

        # Stop Qta to BUY TO Real Free Qta
        try:               
            if quantity_post_size_applied > _symbol_bal_first_free[1]:
                quantity_post_size_applied = _symbol_bal_first_free[1] 
        except Exception:
            _inputs_temp = f"||{type(_symbol_bal_first_free[1])},{_symbol_bal_first_free[1]}|{type(quantity_post_size_applied)},{quantity_post_size_applied}"
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_sell',_inputs+_inputs_temp,traceback.format_exc(2))}")
            return(_response_tuple)

        """ Get Symbol LOT SIZE """
        _symbol_lot_size = self.general_get_symbol_info_filter('LOT_SIZE')
        if _symbol_lot_size[0] != 'OK':
            _response_tuple = ('NOK',  _symbol_lot_size[1])
            return(_response_tuple)

        """ Get Symbol Filter MIN_NOTIONAL """
        _symbol_min_notional = self.general_get_symbol_info_filter('MIN_NOTIONAL')
        if _symbol_min_notional[0] != 'OK':
            _response_tuple = ('NOK',  _symbol_min_notional[1])
            return(_response_tuple)

        """ Get Symbol Avg Price or Symbol Input Price """
        if p_type == 'market':
            _symbol_price = self.general_get_symbol_avg_price() # Avg Price
            if _symbol_price[0] != 'OK':
                _response_tuple = ('NOK',  _symbol_price[1])
                return(_response_tuple)                            
        elif (p_type == 'limit' or p_type == 'stop_limit' or p_type == 'oco') and p_price:
            try:
                _symbol_price = tuple( ( 'OK' , Decimal(p_price) ) ) # Symbol Input Price
            except Exception:
                _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_sell',_inputs,traceback.format_exc(2))}")
                return(_response_tuple)
        else:
            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_quantity_to_sell',_inputs,'p_type unknown or p_price is None')}")
            return(_response_tuple)

        """ Calculate Quantity End """

        _symbol_step_size_value    = _symbol_lot_size[1].get('LOT_SIZE_stepSize')
        _symbol_min_qty_value      = _symbol_lot_size[1].get('LOT_SIZE_minQty')
        _symbol_min_notional_value = _symbol_min_notional[1].get('MIN_NOTIONAL_minNotional')
        _symbol_price_value        = _symbol_price[1]
        
        try:
            quantity_pre_stepSize_applied = Decimal(quantity_post_size_applied)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_quantity_to_sell',_inputs,traceback.format_exc(2))}")
            return(_response_tuple)
        
        # Truncate By Step Size
        quantity_post_stepSize_applied = self.truncate_by_step_size(quantity_pre_stepSize_applied, _symbol_step_size_value)
        if quantity_post_stepSize_applied[0] != 'OK':
            _msg                = quantity_post_stepSize_applied[1]
            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_quantity_to_sell',_inputs,_msg)}")
            return(_response_tuple)            
        
        # Output
        quantity_processed_final = quantity_post_stepSize_applied[1]
        if quantity_processed_final > _symbol_min_qty_value:

            if (_symbol_price_value * quantity_processed_final) > _symbol_min_notional_value:
                _response_tuple = ('OK', tuple(( quantity_processed_final, quantity_pre_size_applied, quantity_post_size_applied )) )
            else:
                _msg                = f"Quantity * Price (= {quantity_pre_stepSize_applied*_symbol_price_value:.10f}) to make SELL is not > Symbol Min Notional Qty (= {_symbol_min_notional_value})"
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_quantity_to_sell',_inputs,_msg)}")

        else:
            _msg                = f"Quantity (= {quantity_pre_stepSize_applied:.10f}) to make SELL is not > Symbol Min Qty (= {_symbol_min_qty_value})"
            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_get_quantity_to_sell',_inputs,_msg)}")


        return(_response_tuple)

    # Set Leverage - only Futures
    def account_set_symbol_leverage(self, p_leverage = 50, p_symbol_input = None):

        # Prepare
        _inputs                 = None 
        _response_tuple         = None                  
        _response               = None
        _symbol_exists          = None
        _symbol_work            = None

        # Choose Symbol
        if not p_symbol_input:
            _symbol_work = self.symbol
        else:
            _symbol_work = p_symbol_input

        # Set Inputs
        _inputs = f"{p_leverage}|{_symbol_work}"

        # Check if Symbol Exists
        _symbol_exists = self.general_check_if_symbol_exists(_symbol_work)
        if _symbol_exists[0] == 'NOK':
            _response_tuple = (_symbol_exists[0],  _symbol_exists[1])
            return(_response_tuple)

        # Set Leverage
        try:
            _response = self.client.futures_change_leverage(symbol=_symbol_work,leverage = p_leverage)
            if _response:
                _response_tuple = ('OK', _response)
            else:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_set_symbol_leverage',_inputs,'_response is None')}")

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except Exception:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_set_symbol_leverage',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)
        



    """ ORDER """

    # Create a Order Wallet --> spot + margin
    def account_create_order(self, p_type, p_side, p_size, p_limit = None, p_stop = None, p_price = None):

        # Prepare
        _inputs                     = f"{self.wallet}|{p_type}|{p_side}|{p_size}|{p_limit}|{p_stop}|{p_price}|{self.symbol_first}|{self.symbol_second}"
        _response_tuple             = None
        _how2get_qta2buy            = 'only_available'
        _quantity_calculated_result = None
        _quantity_to_use            = None
        _quantity_pre_size_applied  = None
        _quantity_post_size_applied = None
        _symbol_exists              = None
        _client_type                = None
        _client_side                = None
        _client_timeinforce         = None
        _what_fee                   = None

        # Check if Symbol Exists
        _symbol_exists = self.general_check_if_symbol_exists()
        if _symbol_exists[0] == 'NOK':
            _response_tuple = ('NOK', _symbol_exists[1])
            return(_response_tuple)

        # Choose TYPE & FEE
        if p_type == 'market':
            _client_type        = self.client.ORDER_TYPE_MARKET
            _what_fee           = 'taker' # --> I'm going to Market so it's a taker
        elif p_type == 'limit':
            _client_type        = self.client.ORDER_TYPE_LIMIT
            _client_timeinforce = self.client.TIME_IN_FORCE_GTC
            _what_fee           = 'maker' # --> I'm going to Price so it's a maker
        elif p_type == 'stop_limit':
            _client_type        = self.client.ORDER_TYPE_STOP_LOSS_LIMIT
            _client_timeinforce = self.client.TIME_IN_FORCE_GTC
            _what_fee           = 'maker' # --> I'm going to Price so it's a maker
        elif p_type == 'oco':
            _client_timeinforce = self.client.TIME_IN_FORCE_GTC
            _what_fee           = 'maker' # --> I'm going to Price so it's a maker
        else:
            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_create_order',_inputs, p_type+' unknown')}")
            return(_response_tuple)

        # Choose SIDE and calculate QUANTITY
        if p_side == 'sell':
            
            _client_side = self.client.SIDE_SELL
            
            if self.wallet != 'futures':
                _quantity_calculated_result = self.account_get_quantity_to_sell(p_type, p_size, p_limit)
                if _quantity_calculated_result[0] == 'OK':
                    _quantity_to_use            = _quantity_calculated_result[1][0]
                    _quantity_pre_size_applied  = _quantity_calculated_result[1][1]
                    _quantity_post_size_applied = _quantity_calculated_result[1][2]
                else:
                    _response_tuple = ('NOK',  _quantity_calculated_result[1])
                    return(_response_tuple)
                    
        elif p_side == 'buy':
            
            _client_side = self.client.SIDE_BUY
            
            if self.wallet != 'futures':
                _quantity_calculated_result = self.account_get_quantity_to_buy(_what_fee, p_type, p_size, _how2get_qta2buy, p_limit)
                if _quantity_calculated_result[0] == 'OK':
                    _quantity_to_use            = _quantity_calculated_result[1][0]
                    _quantity_pre_size_applied  = _quantity_calculated_result[1][1]
                    _quantity_post_size_applied = _quantity_calculated_result[1][2]
                else:
                    _response_tuple = ('NOK',  _quantity_calculated_result[1])
                    return(_response_tuple)
                    
        else:
            _response_tuple = ('NOK', f"{utility.my_log('Error', 'account_create_order', _inputs, p_side+' unknown')}")
            return(_response_tuple)

        # Create ORDER
        if p_type == 'market':

            try:

                if self.wallet == 'spot':

                    _order = self.client.create_order(  symbol      = self.symbol,
                                                        side        = _client_side,
                                                        type        = _client_type,
                                                        quantity    = _quantity_to_use   )
                elif self.wallet == 'margin':

                    _order = self.client.create_margin_order(   symbol      = self.symbol,
                                                                side        = _client_side,
                                                                type        = _client_type,
                                                                quantity    = _quantity_to_use   )
                elif self.wallet == 'futures':
                    
                    _quantity_to_use = p_size
                    
                    _order = self.client.futures_create_order(  symbol      = self.symbol,
                                                                side        = _client_side,
                                                                type        = _client_type,
                                                                quantity    = _quantity_to_use   )

                _response_tuple = ('OK', tuple(( _order, _quantity_pre_size_applied, _quantity_post_size_applied)) )

            except BinanceAPIException as e:
                _error = str(e).split(":")[1]
                _response_tuple = ('NOK',  _error)
            except:
                _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_create_order',_inputs,traceback.format_exc())}")

        elif p_type == 'limit':

            if not p_limit:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_create_order',_inputs,'Order Limit without limit price input')}")
                return(_response_tuple)

            try:

                if self.wallet == 'spot':

                    _order = self.client.create_order(  symbol      = self.symbol,
                                                        side        = _client_side,
                                                        type        = _client_type,
                                                        timeInForce = _client_timeinforce,
                                                        quantity    = _quantity_to_use,
                                                        price       = p_limit    )
                elif self.wallet == 'margin':

                    _order = self.client.create_margin_order(   symbol      = self.symbol,
                                                                side        = _client_side,
                                                                type        = _client_type,
                                                                timeInForce = _client_timeinforce,
                                                                quantity    = _quantity_to_use,
                                                                price       = p_limit    )

                _response_tuple = ('OK', tuple(( _order, _quantity_pre_size_applied, _quantity_post_size_applied)) )

            except BinanceAPIException as e:
                _error = str(e).split(":")[1]
                _response_tuple = ('NOK',  _error)
            except:
                _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_create_order',_inputs,traceback.format_exc())}")

        elif p_type == 'stop_limit':

            if not p_limit:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_create_order',_inputs,'Order Stop Limit without LIMIT input')}")
                return(_response_tuple)

            if not p_stop:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_create_order',_inputs,'Order Stop Limit without STOP input')}")
                return(_response_tuple)

            try:

                if self.wallet == 'spot':

                    _order = self.client.create_order(  symbol      = self.symbol,
                                                        side        = _client_side,
                                                        type        = _client_type,
                                                        timeInForce = _client_timeinforce,
                                                        quantity    = _quantity_to_use,
                                                        price       = p_limit,
                                                        stopPrice   = p_stop )
                elif self.wallet == 'margin':

                    _order = self.client.create_margin_order(   symbol      = self.symbol,
                                                                side        = _client_side,
                                                                type        = _client_type,
                                                                timeInForce = _client_timeinforce,
                                                                quantity    = _quantity_to_use,
                                                                price       = p_limit,
                                                                stopPrice   = p_stop )

                _response_tuple = ('OK', tuple(( _order, _quantity_pre_size_applied, _quantity_post_size_applied)) )

            except BinanceAPIException as e:
                _error = str(e).split(":")[1]
                _response_tuple = ('NOK',  _error)
            except:
                _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_create_order',_inputs,traceback.format_exc())}")

        elif p_type == 'oco':

            if not p_limit:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_create_order',_inputs,'Order OCO without LIMIT input')}")
                return(_response_tuple)

            if not p_stop:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_create_order',_inputs,'Order OCO without STOP input')}")
                return(_response_tuple)

            if not p_price:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_create_order',_inputs,'Order OCO without PRICE input')}")
                return(_response_tuple)

            try:

                if self.wallet == 'spot':

                    _order = self.client.create_oco_order(  symbol                  = self.symbol,
                                                            side                    = _client_side,
                                                            stopLimitTimeInForce    = _client_timeinforce,
                                                            quantity                = _quantity_to_use,
                                                            stopLimitPrice          = p_limit,
                                                            stopPrice               = p_stop,
                                                            price                   = p_price    )

                    _response_tuple = ('OK', tuple(( _order, _quantity_pre_size_applied, _quantity_post_size_applied)) )

                elif self.wallet == 'margin':

                     _response_tuple = ('NOK', f"{ utility.my_log('Error','account_create_order',_inputs,'no margin oco order exist')}" )



            except BinanceAPIException as e:
                _error = str(e).split(":")[1]
                _response_tuple = ('NOK',  _error)
            except:
                _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_create_order',_inputs,traceback.format_exc())}")

        else:

            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_create_order',_inputs,'p_type unknown')}")

        return(_response_tuple)

    # Get Account Open Orders
    def account_get_open_orders(self, p_symbol_input = None):

        # Prepare
        _inputs         = f"{self.wallet}|{p_symbol_input}"
        _response_tuple = None
        _my_openorders  = None

        try:
            if not p_symbol_input:
                if self.wallet == 'spot':
                    _my_openorders  = self.client.get_open_orders()
                elif self.wallet == 'margin':
                    _my_openorders  = self.client.get_open_margin_orders()
                elif self.wallet == 'futures':
                    _my_openorders  = self.client.futures_get_open_orders()                    
                _response_tuple = ('OK', _my_openorders)
            else:
                if self.wallet == 'spot':
                    _my_openorders  = self.client.get_open_orders(symbol=p_symbol_input)
                elif self.wallet == 'margin':
                    _my_openorders  = self.client.get_open_margin_orders(symbol=p_symbol_input)
                elif self.wallet == 'futures':
                    _my_openorders  = self.client.futures_get_open_orders(symbol=p_symbol_input)                      
                _response_tuple = ('OK', _my_openorders)

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_get_open_orders',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)

    # Get Open Account Position Info - ONLY Futures
    def account_get_open_position_information(self, p_symbol_input = None):

        # Prepare
        _inputs         = f"{self.wallet}|{p_symbol_input}"
        _response_tuple = None
        _my_positions   = None

        try:
            if not p_symbol_input:
                if self.wallet == 'spot':
                    _self.response_tuple = ('NOK',  'No position Info for Spot Wallet')
                elif self.wallet == 'margin':
                    _self.response_tuple = ('NOK',  'No position Info for Margin Wallet')
                elif self.wallet == 'futures':
                    _my_positions  = self.client.futures_position_information()                    
                _response_tuple = ('OK', _my_positions)
            else:
                if self.wallet == 'spot':
                    _self.response_tuple = ('NOK',  'No position Info for Spot Wallet')
                elif self.wallet == 'margin':
                    _self.response_tuple = ('NOK',  'No position Info for Margin Wallet')
                elif self.wallet == 'futures':
                    _my_positions  = self.client.futures_position_information(symbol=p_symbol_input)                      
                _response_tuple = ('OK', _my_positions)

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','get_position_information',_inputs,traceback.format_exc(2))}")

        return(_response_tuple)

    # Cancel a Account Order
    def account_cancel_order(self, p_symbol_input, p_orderid):

        # Prepare
        _inputs         = f"{self.wallet}|{p_symbol_input}|{p_orderid}"
        _response_tuple = None        
        _result_raw     = None

        try:
            if self.wallet == 'spot':
                _result_raw = self.client.cancel_order( symbol = p_symbol_input, orderId =p_orderid)
            elif self.wallet == 'margin':
                _result_raw = self.client.cancel_margin_order( symbol = p_symbol_input, orderId =p_orderid)
            elif self.wallet == 'futures':
                _result_raw = self.client.futures_cancel_order( symbol = p_symbol_input, orderId =p_orderid)                
            _response_tuple = ('OK', _result_raw)

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
        except:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_cancel_order',_inputs,traceback.format_exc())}")

        return(_response_tuple)

    # Convert Dust to BNB
    def account_convert_dust2bnb(self, p_symbol_input):

        # Prepare
        _inputs             = f"{self.wallet}|{p_symbol_input}"
        _response_tuple     = None        
        _result_raw         = None
        _result_nice        = None
        _transfer_result    = None
        _symbol_input_clean = None
        _tot_gross          = 0
        _fee                = 0
        _tot_net            = 0
        _asset_qta          = 0
        
        # Check if wallet is Margin
        if self.wallet == 'margin':
            _response_tuple = ('NOK', f"{ utility.my_log('Error','account_convert_dust2bnb',_inputs,'no margin convert 2 bnb exist')}")
            return(_response_tuple)
        
        # Work
        try:
            _symbol_input_clean = p_symbol_input.upper()
            _result_raw = self.client.transfer_dust(asset=_symbol_input_clean)

        except BinanceAPIException as e:
            _error = str(e).split(":")[1]
            _response_tuple = ('NOK',  _error)
            return(_response_tuple)
        except:
            _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_convert_dust2bnb',_inputs,traceback.format_exc(2))}")
            return(_response_tuple)
        
        # Format
        if _result_raw:
            
            try:
                _tot_gross  = Decimal(_result_raw.get('totalTransfered'))
                _fee        = Decimal(_result_raw.get('totalServiceCharge'))
                _tot_net    = _tot_gross - _fee
    
                for _transfer_result in _result_raw.get('transferResult'):
                    if _transfer_result:
                        _asset_qta  = _asset_qta + Decimal(_transfer_result.get('amount'))
            except:
                _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_convert_dust2bnb',_inputs,traceback.format_exc(2))}")
                return(_response_tuple)

            _result_nice  = f"Dust Asset: {_symbol_input_clean} {chr(10)}"\
                            f"Dust Qta  : {_asset_qta} {chr(10)}"\
                            f"--------{chr(10)}"\
                            f"BNB Gross: {_tot_gross} {chr(10)}"\
                            f"BNB Fee  : {_fee}{chr(10)}"\
                            f"BNB Net  : {_tot_net} {chr(10)}"

            _response_tuple = ('OK', _result_nice)

        else:

            _response_tuple = ('NOK',  f"{ utility.my_log('Error','spot_convert_dust2bnb',_inputs,'_result_raw is None')}")

        return(_response_tuple)


    """ FORMAT BINANCE RESULT """

    # Format Spot & Margin Open Orders Results
    def account_format_open_orders_result(self, p_result):

        # Prepare
        _inputs         = f"{p_result}"
        _response_tuple = None        
        _dict_result    = {}        
        _type           = None
        _date           = None
        _orderListId    = None                      
        _list_output    = []

        # Build Output --> for each order found
        for _dict_result in p_result:

            # Get Type
            if _dict_result.get('type'):            
                _type = _dict_result.get('type').upper()
            
            # Get&Format Date
            if _dict_result.get('time'):
                _date = utility.timestamp_formatter(_dict_result.get('time'))

            # Get orderListId for OCO Order
            if _dict_result.get('orderListId') != -1:
                _orderListId = _dict_result.get('orderListId')

            """ COMMON """
            _row0   = f"Date: {_date}"
            _row1   = f"ExchangeOrderID: {_dict_result.get('orderId')}"
            _row3   = f"Symbol: {_dict_result.get('symbol')}"
            if self.wallet == 'futures':
                _row4 = f"Side: {'LONG' if _dict_result.get('side') == 'BUY' else 'SHORT'}"
            else:
                _row4 = f"Side: {_dict_result.get('side')}"
            _row5   = f"Quantity: {_dict_result.get('origQty')}"
            
            # Build Output
            if _type == 'MARKET': # MARKET TYPE ORDER 

                _row_m_2    =   f"Type: Market"

                _message    =   f"{_row0} {chr(10)}"\
                                f"{_row1} {chr(10)}"\
                                f"{_row_m_2} {chr(10)}"\
                                f"{_row3} {chr(10)}"\
                                f"{_row4} {chr(10)}"\
                                f"{_row5}"

            elif _type == 'LIMIT' or _type == 'LIMIT_MAKER': # LIMIT TYPE ORDER 

                _row_l_2        =   f"Type: Limit"
                _row_l_6        =   f"Price: {_dict_result.get('price')}"
                _row_o_0        =   f"OrderOCOId: {_orderListId}" # For OCO Order               

                if _orderListId:
                    _message    =   f"{_row0} {chr(10)}"\
                                    f"{_row_o_0} {chr(10)}"\
                                    f"{_row1} {chr(10)}"\
                                    f"{_row_l_2} {chr(10)}"\
                                    f"{_row3} {chr(10)}"\
                                    f"{_row4} {chr(10)}"\
                                    f"{_row5} {chr(10)}"\
                                    f"{_row_l_6}"
                else:
                    _message    =   f"{_row0} {chr(10)}"\
                                    f"{_row1} {chr(10)}"\
                                    f"{_row_l_2} {chr(10)}"\
                                    f"{_row3} {chr(10)}"\
                                    f"{_row4} {chr(10)}"\
                                    f"{_row5} {chr(10)}"\
                                    f"{_row_l_6}"

            elif _type == 'STOP_LOSS_LIMIT': # STOP LIMIT TYPE ORDER 

                _row_sl_2   =   f"Type: Stop-Limit"
                _row_sl_6   =   f"Price: {_dict_result.get('price')}"
                _row_sl_7   =   f"Stop: {_dict_result.get('stopPrice')}"
                _row_o_0    =   f"OrderOCOId: {_orderListId}"  # For OCO Order  

                if _orderListId:
                    _message    =   f"{_row0} {chr(10)}"\
                                    f"{_row_o_0} {chr(10)}"\
                                    f"{_row1} {chr(10)}"\
                                    f"{_row_sl_2} {chr(10)}"\
                                    f"{_row3} {chr(10)}"\
                                    f"{_row4} {chr(10)}"\
                                    f"{_row5} {chr(10)}"\
                                    f"{_row_sl_6} {chr(10)}"\
                                    f"{_row_sl_7}"
                else:
                    _message    =   f"{_row0} {chr(10)}"\
                                    f"{_row1} {chr(10)}"\
                                    f"{_row_sl_2} {chr(10)}"\
                                    f"{_row3} {chr(10)}"\
                                    f"{_row4} {chr(10)}"\
                                    f"{_row5} {chr(10)}"\
                                    f"{_row_sl_6} {chr(10)}"\
                                    f"{_row_sl_7}"

            elif _type == 'STOP' or _type == 'TAKE_PROFIT': # FUTURES - STOP LIMIT LONG (STOP) & SHORT (TAKE_PROFIT) TYPE ORDER 

                _row_sl_2   =   f"Type: Stop-Limit"
                _row_sl_6   =   f"Price: {_dict_result.get('price')}"
                _row_sl_7   =   f"Stop: {_dict_result.get('stopPrice')}" 

                _message    =   f"{_row0} {chr(10)}"\
                                f"{_row1} {chr(10)}"\
                                f"{_row_sl_2} {chr(10)}"\
                                f"{_row3} {chr(10)}"\
                                f"{_row4} {chr(10)}"\
                                f"{_row5} {chr(10)}"\
                                f"{_row_sl_6} {chr(10)}"\
                                f"{_row_sl_7}"

            elif _type == 'STOP_MARKET' or _type == 'TAKE_PROFIT_MARKET': # FUTURES - STOP MARKET LONG (STOP_MARKET) & SHORT (TAKE_PROFIT_MARKET) TYPE ORDER 

                _row_sm_2   =   f"Type: Stop-Market"
                _row_sm_7   =   f"Stop: {_dict_result.get('stopPrice')}" 

                _message    =   f"{_row0} {chr(10)}"\
                                f"{_row1} {chr(10)}"\
                                f"{_row_sm_2} {chr(10)}"\
                                f"{_row3} {chr(10)}"\
                                f"{_row4} {chr(10)}"\
                                f"{_row5} {chr(10)}"\
                                f"{_row_sm_7}"

            else:

                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_format_open_orders_result',_inputs,_type+' _type unknown ')}")
                return(_response_tuple)

            # Add Message on List
            _list_output.append(_message)
        
        # Output
        _response_tuple = ('OK', _list_output)

        return(_response_tuple)

    # Format Spot & Margin Order Result
    def account_format_create_order_result(self, p_result, p_cancel = False, p_type = None):

        # Prepare
        _inputs         = f"{p_result}|{p_cancel}|{p_type}"
        _response_tuple = None        
        _type           = None
        _date           = None
        _temp1          = None
        _temp2          = None
        
        # Decimal digit
        getcontext().prec = 8

        # Get&Build Type
        if p_type == 'stop_limit': # --> The type is not written on the output of a STOP_LOSS_LIMIT Order
            _type = 'STOP_LOSS_LIMIT'
        elif p_type == 'oco': # --> The type are 2 on the output of a OCO Order
            _type = 'OCO'
        else:
            if p_result.get('type'):
                _type = p_result.get('type').upper()
            else:
                _type = 'OCO'

        # Get&Format Date
        if _type == 'OCO':
            if p_result.get('transactionTime'):
                _date = utility.timestamp_formatter(p_result.get('transactionTime'))
        else:
            if p_result.get('transactTime'):
                _date = utility.timestamp_formatter(p_result.get('transactTime'))

        # If Filled Build Price & Fee
        if p_result.get('status') == 'FILLED':

            # Prepare
            _price          = 0           
            _qty            = 0
            _price_qty      = 0
            _price_qty_tot  = 0
            _qty_tot        = 0
            _price_avg      = 0
            _fee            = 0
            _fill           = None
            _fee_symbol     = None
            
            try:
                
                for _fill in p_result.get('fills'):
                    
                    # Get & Trasform & Cumulate
                    if _fill.get('price'):
                        _price = Decimal(_fill.get('price'))
                    if _fill.get('qty'):
                        _qty = Decimal(_fill.get('qty'))
                    if _fill.get('commission'):
                        _fee = _fee + Decimal(_fill.get('commission'))
                        
                    _fee_symbol = _fill.get('commissionAsset')
    
                    # Calculate
                    _price_qty      = _price * _qty
                    _price_qty_tot  = _price_qty + _price_qty
                    _qty_tot        = _qty + _qty
    
                # Weighted average - Media Ponderata
                if _price_qty_tot != 0 and _qty_tot != 0:
                    _price_avg = _price_qty_tot / _qty_tot

            except:
                _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_format_create_order_result',_inputs,traceback.format_exc())}")
                return(_response_tuple)

        # Common
        _row1   = f"Date: {_date}"
        _row2   = f"Status: {p_result.get('status')}"
        _row3   = f"Order Id: {p_result.get('orderId')}"
        _row5   = f"Symbol: {p_result.get('symbol')}"
        if self.wallet == 'futures':
            _row6 = f"Side: {'LONG' if p_result.get('side') == 'BUY' else 'SHORT'}"
        else:
            _row6 = f"Side: {p_result.get('side')}"

        # Build Output
        if _type == 'MARKET': # MARKET ORDER TYPE  

            # Build Rows
            if p_result.get('side').upper() == 'BUY':
                _temp1 = "Quantity Buyed"
                _temp2 = "Cost"
            elif p_result.get('side').upper() == 'SELL':
                _temp1 = "Quantity Sold"
                _temp2 = "Revenue"
            else:
                _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_format_create_order_result',_inputs,'Side unknown')}")
                return(_response_tuple)

            _row_m_4 = f"Type: Market"
            _row_m_7 = f"Price: {_price_avg}"
            _row_m_8 = f"Fee paid in {_fee_symbol}: {_fee}"
            
            try:
                if p_result.get('executedQty'):
                    _row_m_9    = f"{_temp1}: {Decimal(p_result.get('executedQty'))}"
                else:
                    _row_m_9    = f"{_temp1}: {p_result.get('executedQty')}"
                if p_result.get('cummulativeQuoteQty'):
                    _row_m_10   = f"{_temp2}: {Decimal(p_result.get('cummulativeQuoteQty'))}"
                else:
                    _row_m_10   = f"{_temp2}: {p_result.get('cummulativeQuoteQty')}"
            except:
                _response_tuple = ('NOK',  f"{ utility.my_log('Exception','account_format_create_order_result',_inputs,traceback.format_exc())}")
                return(_response_tuple)
                
            # Build Message
            _message =  f"{_row1} {chr(10)}"\
                        f"{_row2} {chr(10)}"\
                        f"{_row3} {chr(10)}"\
                        f"{_row_m_4} {chr(10)}"\
                        f"{_row5} {chr(10)}"\
                        f"{_row6} {chr(10)}"\
                        f"{_row_m_7} {chr(10)}"\
                        f"{_row_m_8} {chr(10)}"\
                        f"{_row_m_9} {chr(10)}"\
                        f"{_row_m_10}"

        elif _type == 'LIMIT': # LIMIT ORDER TYPE 

            # Build Rows            
            _row_l_4 = f"Type: Limit"
            _row_l_7 = f"Limit: {p_result.get('price')}"
            _row_l_8 = f"Quantity: {p_result.get('origQty')}"

            # Build Message
            if not p_cancel:
                _message =  f"{_row1} {chr(10)}"\
                            f"{_row2} {chr(10)}"\
                            f"{_row3} {chr(10)}"\
                            f"{_row_l_4} {chr(10)}"\
                            f"{_row5} {chr(10)}"\
                            f"{_row6} {chr(10)}"\
                            f"{_row_l_7} {chr(10)}"\
                            f"{_row_l_8}"
            else:
                _message =  f"{_row2} {chr(10)}"\
                            f"{_row3} {chr(10)}"\
                            f"{_row_l_4} {chr(10)}"\
                            f"{_row5} {chr(10)}"\
                            f"{_row6} {chr(10)}"\
                            f"{_row_l_7} {chr(10)}"\
                            f"{_row_l_8}"

        elif _type == 'STOP_LOSS_LIMIT': # STOP LIMIT ORDER TYPE  

            """
            The output of a Stop-Limit is very poor .. for this i show very little.
            Example of output: {'symbol': 'BTCUSDT', 'orderId': 2786196182, 'orderListId': -1, 'clientOrderId': 'p0qTfCHG0tAxFoivBqqI72', 'transactTime': 1596104181799}
            """

            # Build Rows
            _row_sl_2   =   f"Status: NEW"
            _row_sl_4   =   f"Type: Stop-Limit"

            # Build Message
            if not p_cancel:
                _message    =   f"{_row1} {chr(10)}"\
                                f"{_row_sl_2} {chr(10)}"\
                                f"{_row3} {chr(10)}"\
                                f"{_row_sl_4} {chr(10)}"\
                                f"{_row5}"
            else:
                _row_sl_7   =   f"Stop: {p_result.get('stopPrice')}"
                _row_sl_8   =   f"Limit: {p_result.get('price')}"
                _row_sl_9   =   f"Quantity: {p_result.get('origQty')}"
                _message    =   f"{_row2} {chr(10)}"\
                                f"{_row3} {chr(10)}"\
                                f"{_row_sl_4} {chr(10)}"\
                                f"{_row5} {chr(10)}"\
                                f"{_row6} {chr(10)}"\
                                f"{_row_sl_7} {chr(10)}"\
                                f"{_row_sl_8} {chr(10)}"\
                                f"{_row_sl_9}"

        elif _type == 'OCO': # OCO ORDER TYPE: Stop-Limit + Limit 

            # Build Rows
            _title0     = ">> Order OCO <<"
            _row_o_1    = _row1
            _row_o_2    = f"Order Id: {p_result.get('orderListId')}"
            _row_o_3    = f"Symbol: {p_result.get('symbol')}"
            _row_o_4    = f"Side: {p_result.get('orderReports')[0].get('side')}"
            _row_o_5    = f"Quantity: {p_result.get('orderReports')[0].get('origQty')}"

            _title1     = "> Stop Limit"
            _row_o_6    = f"Status: {p_result.get('orderReports')[0].get('status')}"
            _row_o_7    = f"Order Id: {p_result.get('orderReports')[0].get('orderId')}"
            _row_o_8    = f"Type: {p_result.get('orderReports')[0].get('type')}"
            _row_o_9    = f"Stop: {p_result.get('orderReports')[0].get('stopPrice')}"
            _row_o_10   = f"Limit: {p_result.get('orderReports')[0].get('price')}"

            _title2     = "> Limit"
            _row_o_11   = f"Status: {p_result.get('orderReports')[1].get('status')}"
            _row_o_12   = f"Order Id: {p_result.get('orderReports')[1].get('orderId')}"
            _row_o_13   = f"Type: {p_result.get('orderReports')[1].get('type')}"
            _row_o_14   = f"Limit: {p_result.get('orderReports')[1].get('price')}"

            # Build Message                                
            _message =  f"{_title0} {chr(10)}"\
                        f"{_row_o_1} {chr(10)}"\
                        f"{_row_o_2} {chr(10)}"\
                        f"{_row_o_3} {chr(10)}"\
                        f"{_row_o_4} {chr(10)}"\
                        f"{_row_o_5} {chr(10)}"\
                        f"{_title1} {chr(10)}"\
                        f"{_row_o_6} {chr(10)}"\
                        f"{_row_o_7} {chr(10)}"\
                        f"{_row_o_8} {chr(10)}"\
                        f"{_row_o_9} {chr(10)}"\
                        f"{_row_o_10} {chr(10)}"\
                        f"{_title2} {chr(10)}"\
                        f"{_row_o_11} {chr(10)}"\
                        f"{_row_o_12} {chr(10)}"\
                        f"{_row_o_13} {chr(10)}"\
                        f"{_row_o_14}"

        elif _type == 'STOP' or _type == 'TAKE_PROFIT': # FUTURES - STOP LIMIT LONG (STOP) & SHORT (TAKE_PROFIT) TYPE ORDER
            
            # Build Rows
            #_row_sl_2   =   f"Status: NEW"
            _row_sl_4   =   f"Type: Stop-Limit"

            # Build Message
            if not p_cancel:
                pass
            else:
                _row_sl_7   =   f"Stop: {p_result.get('stopPrice')}"
                _row_sl_8   =   f"Limit: {p_result.get('price')}"
                _row_sl_9   =   f"Quantity: {p_result.get('origQty')}"
                _message    =   f"{_row2} {chr(10)}"\
                                f"{_row3} {chr(10)}"\
                                f"{_row_sl_4} {chr(10)}"\
                                f"{_row5} {chr(10)}"\
                                f"{_row6} {chr(10)}"\
                                f"{_row_sl_7} {chr(10)}"\
                                f"{_row_sl_8} {chr(10)}"\
                                f"{_row_sl_9}"
            
        elif _type == 'STOP_MARKET' or _type == 'TAKE_PROFIT_MARKET': # FUTURES - STOP MARKET LONG (STOP_MARKET) & SHORT (TAKE_PROFIT_MARKET) TYPE ORDER 
            
            # Build Rows
            #_row_sl_2   =   f"Status: NEW"
            _row_sl_4   =   f"Type: Stop-Market"

            # Build Message
            if not p_cancel:
                pass
            else:
                _row_sl_7   =   f"Stop: {p_result.get('stopPrice')}"
                _row_sl_9   =   f"Quantity: {p_result.get('origQty')}"
                _message    =   f"{_row2} {chr(10)}"\
                                f"{_row3} {chr(10)}"\
                                f"{_row_sl_4} {chr(10)}"\
                                f"{_row5} {chr(10)}"\
                                f"{_row6} {chr(10)}"\
                                f"{_row_sl_7} {chr(10)}"\
                                f"{_row_sl_9}"
            
        else:

            _response_tuple = ('NOK',  f"{ utility.my_log('Error','account_format_create_order_result',_inputs,_type+' _type unknown')}")
            return(_response_tuple)

        # Output
        _response_tuple = ('OK', _message)

        return(_response_tuple)

    # Format Futures Open Positions Results
    def account_format_open_position_result(self, p_result):

        # Prepare
        _inputs         = None
        _response_tuple = None        
        _dict_result    = {}
        _list_output    = []      
        
        # Specific
        _entry_price        = None
        _leverage           = None
        _liquidation_price  = None
        _mark_price         = None
        _qta                = 0
        _margin             = 0
        _margin_temp_1      = None
        _margin_temp_2      = None          
        _side               = None
        _symbol             = None
        _pnl                = None
        _pnl_perc           = None 
        _pnl_perc_temp_1    = None 
        _pnl_perc_temp_2    = None                              
        
        # Build Output --> for each position found
        for _dict_result in p_result:
            
            # Prepare _qta
            if _dict_result.get('positionAmt'):
                try:
                    _qta = Decimal(_dict_result.get('positionAmt'))
                except Exception:
                    _inputs      = f"{_dict_result}"
                    _inputs_temp = f"||{type(_dict_result.get('positionAmt'))},{_dict_result.get('positionAmt')}"
                    _response_tuple = ('NOK', f"{ utility.my_log('Exception','account_format_open_position_result',_inputs+_inputs_temp,traceback.format_exc(2))}")
                    return(_response_tuple)

            # Only position with something
            if _qta != 0:
                
                """ Calculate MARGIN """
                try:
                    _margin_temp_1 = abs(_qta) * Decimal(_dict_result.get('markPrice'))
                except Exception:
                    _inputs      = f"{_dict_result}"
                    _inputs_temp = f"||{type(_qta)},{_qta}|{type(_dict_result.get('entryPrice'))},{_dict_result.get('entryPrice')}"
                    _response_tuple = ('NOK', f"{ utility.my_log('Exception','account_format_open_position_result',_inputs+_inputs_temp,traceback.format_exc(2))}")
                    return(_response_tuple)

                try:
                    _margin_temp_2 = _margin_temp_1 / Decimal(_dict_result.get('leverage'))
                except Exception:
                    _inputs      = f"{_dict_result}"
                    _inputs_temp = f"||{type(_margin_temp_1)},{_margin_temp_1}|{type(_dict_result.get('leverage'))},{_dict_result.get('leverage')}"
                    _response_tuple = ('NOK', f"{ utility.my_log('Exception','account_format_open_position_result',_inputs+_inputs_temp,traceback.format_exc(2))}")
                    return(_response_tuple)

                try:
                    _margin = round(_margin_temp_2,2)
                except Exception:
                    _inputs      = f"{_dict_result}"
                    _inputs_temp = f"||{type(_margin_temp_2)},{_margin_temp_2}"
                    _response_tuple = ('NOK', f"{ utility.my_log('Exception','account_format_open_position_result',_inputs+_inputs_temp,traceback.format_exc(2))}")
                    return(_response_tuple)

                """ Calculate PNL % or ROE % """
                try:
                    _pnl_perc_temp_1 = Decimal(_dict_result.get('unRealizedProfit')) * Decimal('100')
                except Exception:
                    _inputs      = f"{_dict_result}"
                    _inputs_temp = f"||{type(_dict_result.get('unRealizedProfit'))},{_dict_result.get('unRealizedProfit')}"
                    _response_tuple = ('NOK', f"{ utility.my_log('Exception','account_format_open_position_result',_inputs+_inputs_temp,traceback.format_exc(2))}")
                    return(_response_tuple)

                try:
                    _pnl_perc_temp_2 = _pnl_perc_temp_1 / _margin
                except Exception:
                    _inputs      = f"{_dict_result}"
                    _inputs_temp = f"||{type(_pnl_perc_temp_1)},{_pnl_perc_temp_1}|{type(_margin)},{_margin}"
                    _response_tuple = ('NOK', f"{ utility.my_log('Exception','account_format_open_position_result',_inputs+_inputs_temp,traceback.format_exc(2))}")
                    return(_response_tuple)

                try:
                    _pnl_perc = round(_pnl_perc_temp_2,2)
                except Exception:
                    _inputs      = f"{_dict_result}"
                    _inputs_temp = f"||{type(_pnl_perc_temp_2)},{_pnl_perc_temp_2}"
                    _response_tuple = ('NOK', f"{ utility.my_log('Exception','account_format_open_position_result',_inputs+_inputs_temp,traceback.format_exc(2))}")
                    return(_response_tuple)

                # Get Values
                _entry_price        = _dict_result.get('entryPrice')              
                _leverage           = _dict_result.get('leverage')
                _liquidation_price  = _dict_result.get('liquidationPrice')
                _mark_price         = _dict_result.get('markPrice')
                _side               = 'LONG' if _qta > 0 else 'SHORT'
                _symbol             = _dict_result.get('symbol')
                _pnl                = _dict_result.get('unRealizedProfit')               

                # Build Output
                _row1   = f"Symbol: {_symbol}"
                _row2   = f"Side: {_side}"
                _row3   = f"Quantity: {_qta}"
                _row4   = f"Leverage: {_leverage}x"            
                _row5   = f"Entry Price: {_entry_price}"
                _row6   = f"Mark Price: {_mark_price}"
                _row7   = f"Liq.Price: {_liquidation_price}"
                _row8   = f"Margin: {_margin}"
                _row9   = f"PNL(ROE %): {_pnl} ({_pnl_perc}%)"
                
                _message =  f"{_row1} {chr(10)}"\
                            f"{_row2} {chr(10)}"\
                            f"{_row3} {chr(10)}"\
                            f"{_row4} {chr(10)}"\
                            f"{_row5} {chr(10)}"\
                            f"{_row6} {chr(10)}"\
                            f"{_row7} {chr(10)}"\
                            f"{_row8} {chr(10)}"\
                            f"{_row9} {chr(10)}"
        
                # Add Message on List
                _list_output.append(_message)
        
        # Output
        _response_tuple = ('OK', _list_output)

        return(_response_tuple)