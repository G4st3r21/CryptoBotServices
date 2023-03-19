from httpx import AsyncClient
import ccxt
import Pair


class MarketsAPI:
    def __init__(self):
        self.exchanges_prices = [
            ('binance', 'https://api.binance.com/api/v3/ticker/price'),
            ('huobi', 'https://api.huobi.pro/market/tickers'),
            ('kucoin', 'https://api.kucoin.com/api/v1/market/allTickers')
        ]

        self.exchanges_pairs = [
            ('binance', 'https://api.huobi.pro/market/trade?symbol='),
            ('huobi', 'https://api.binance.com/api/v3/ticker/bookTicker?symbol='),
            ('kucoin', 'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=')
        ]

        self.binance_api_key = 'KMbXaViQFaveESjhjpeIdOCyzIPaCajBAanvikxe2u7Mc9ePaI8R6IcgZd3snM22'
        self.huobi_api_key = 'c9a8136c-3d2xc4v5bu-9da32c9b-e5cfd'
        self.huobi_api_secret_key = '8693557b-ca14cba2-691ad3f6-09a24'
        self.kucoin_api_key = '63fb9b88365bea000180c10e'

    # async def get_huobi_url(self, symbol):
    #     url = f"https://api.huobi.pro/market/trade?symbol={symbol}"
    #     timestamp = str(int(time.time() * 1000))
    #     sign_str = f"GET\napi.huobi.pro\n{url}\n"
    #     query_string = f"AccessKeyId={self.huobi_api_key}&SignatureMethod=" \
    #                    f"HmacSHA256&SignatureVersion=2&Timestamp={timestamp}"
    #     sign_str += query_string
    #     digest = hmac.new(
    #         self.huobi_api_secret_key.encode("utf-8"),
    #         sign_str.encode("utf-8"), hashlib.sha256
    #     ).hexdigest()
    #     signature = digest.encode("utf-8")
    #     query_string += f"&Signature={signature.decode('utf-8')}"
    #
    #     return f"{url}&{query_string}"

    async def fetch_binance_symbols(self):
        async with AsyncClient() as session:
            response = await session.get(self.exchanges_prices[0][-1])
            data = response.json()
            pairs = []
            prices = {}
            for symbol in data:
                pair = Pair()
                pair = symbol['symbol']
                buy, sell = float(symbol['price']), float(symbol['price'])
                pairs.append(pair)
                prices[pair] = (symbol['symbol'], buy, sell)

            return pairs, prices

    async def fetch_huobi_symbols(self):
        async with AsyncClient() as session:
            response = await session.get(self.exchanges_prices[1][-1])
            data = response.json()
            pairs = []
            prices = {}
            for symbol in data['data']:
                pair = symbol['symbol'].upper()
                buy = float(symbol['ask'])
                sell = float(symbol['bid'])
                pairs.append(pair)
                prices[pair] = (symbol['symbol'], buy, sell)

            return pairs, prices

    async def fetch_kucoin_symbols(self):
        async with AsyncClient() as session:
            response = await session.get(self.exchanges_prices[2][-1])
            data = response.json()
            pairs = []
            prices = {}
            for symbol in data['data']['ticker']:
                pair = symbol['symbol'].replace("-", "")
                buy = float(symbol['sell'])
                sell = float(symbol['buy'])
                pairs.append(pair)
                prices[pair] = (symbol['symbol'], buy, sell)

            return pairs, prices

    async def get_all_prices(self, chosen_exchanges):
        # получаем список торговых пар для каждой биржи
        all_exchanges = {}
        if "binance" in chosen_exchanges:
            all_exchanges["binance"] = await self.fetch_binance_symbols()
        if "huobi" in chosen_exchanges:
            all_exchanges["huobi"] = await self.fetch_huobi_symbols()
        if "kucoin" in chosen_exchanges:
            all_exchanges["kucoin"] = await self.fetch_kucoin_symbols()

        # находим общие торговые пары для всех бирж
        return set.intersection(*map(set, [exchanges[0] for exchanges in all_exchanges.values()])), all_exchanges

    @staticmethod
    async def get_buy_sell_prices(all_exchanges, common_pairs):
        # создаем словарь, где ключ - общая пара, а значение - список цен на каждой бирже
        price_dict = {
            Pair(
                'buy': [
                    [key, exchanges[-1][pair][0], exchanges[-1][pair][1]]
                    for key, exchanges in all_exchanges.items()
                ],
                'sell': [
                    [key, exchanges[-1][pair][0], exchanges[-1][pair][-1]]
                    for key, exchanges in all_exchanges.items()
                ]
        )
            for pair in common_pairs
        }

        # находим цену покупки и продажи на каждой бирже для каждой общей пары
        buy_sell_prices = {}
        for pair, prices in price_dict.items():
            min_price = min(prices['buy'], key=lambda x: x[-1])
            max_price = max(prices['sell'], key=lambda x: x[-1])
            buy_sell_prices[pair] = {
                "valid_symbols": [min_price[1], max_price[1]],
                'buy_price': min_price[-1], 'buy_exchange': min_price[0],
                'sell_price': max_price[-1], 'sell_exchange': max_price[0]
            }
        return buy_sell_prices

    @staticmethod
    async def calculate_arbitrage(buy_sell_prices):
        starting_asset = 1000

        # находим арбитраж на каждой общей паре
        arb_pairs = {
            "0.9-3": [],
            "3-5": [],
            "5-8": [],
            "8+": []
        }
        for pair, prices in buy_sell_prices.items():
            buy_exchange = prices['buy_exchange']
            sell_exchange = prices['sell_exchange']
            buy_price = prices['buy_price']
            sell_price = prices['sell_price']
            arbitrage = (sell_price / buy_price - 1) * 100
            if 0.9 < arbitrage < 3:
                arb_pairs["0.9-3"].append({
                    'pair': pair, 'valid_symbols': prices['valid_symbols'],
                    'buy_exchange': buy_exchange, 'sell_exchange': sell_exchange, 'arbitrage': arbitrage,
                    'starting_asset': starting_asset, 'usd_value': starting_asset / buy_price * 0.998
                })
            elif 3 <= arbitrage < 5:
                arb_pairs["3-5"].append({
                    'pair': pair, 'valid_symbols': prices['valid_symbols'],
                    'buy_exchange': buy_exchange, 'sell_exchange': sell_exchange, 'arbitrage': arbitrage,
                    'starting_asset': starting_asset, 'usd_value': starting_asset / buy_price * 0.998
                })
            elif 5 <= arbitrage < 8:
                arb_pairs["5-8"].append({
                    'pair': pair, 'valid_symbols': prices['valid_symbols'],
                    'buy_exchange': buy_exchange, 'sell_exchange': sell_exchange, 'arbitrage': arbitrage,
                    'starting_asset': starting_asset, 'usd_value': starting_asset / buy_price * 0.998
                })
            elif arbitrage >= 8:
                arb_pairs["8+"].append({
                    'pair': pair, 'valid_symbols': prices['valid_symbols'],
                    'buy_exchange': buy_exchange, 'sell_exchange': sell_exchange, 'arbitrage': arbitrage,
                    'starting_asset': starting_asset, 'usd_value': starting_asset / buy_price * 0.998
                })
        arb_pairs["0.9-3"].sort(reverse=True, key=lambda x: x['arbitrage'])
        arb_pairs["3-5"].sort(reverse=True, key=lambda x: x['arbitrage'])
        arb_pairs["5-8"].sort(reverse=True, key=lambda x: x['arbitrage'])
        arb_pairs["8+"].sort(reverse=True, key=lambda x: x['arbitrage'])

        return arb_pairs

    # TODO: дописать функцию валидности пар
    @staticmethod
    async def check_pair_validity(pairs: list[dict]):
        exchange_names = ['huobipro', 'binance', 'kucoin']
        valid_pairs = []

        for pair in pairs:
            symbol = pair['valid_symbols']  # symbol format - "AAAA/BBBB"
            for exchange_name in exchange_names:
                exchange = ccxt.__getattribute__(exchange_name)()

                try:
                    orderbook = exchange.fetch_order_book(symbol)
                    bid_price = orderbook['bids'][0][0] if len(orderbook['bids']) > 0 else None
                    ask_price = orderbook['asks'][0][0] if len(orderbook['asks']) > 0 else None

                    if bid_price is not None and ask_price is not None:
                        print(f"{exchange_name}: Buy {symbol} at {ask_price}, Sell {symbol} at {bid_price}")
                        valid_pairs.append(pair)
                    else:
                        print(f"{exchange_name}: {symbol} is not tradable")

                except ccxt.ExchangeError:
                    print(f"{exchange_name}: {symbol} is not supported on this exchange")

        return valid_pairs
