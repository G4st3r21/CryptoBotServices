import asyncio
import textwrap

import ccxt.async_support as ccxt
from aiogram.types import Message
from aiogram.utils.exceptions import MessageNotModified
from ccxt import RequestTimeout

from APIs.PairList import PairList, Pair


class CcxtAPI:
    states = [
        1, 2, 3, 4
    ]

    def __init__(self, msg: [Message, None] = None):
        self.pair_list: PairList = PairList()
        self.markets = None
        self.tickers = None

        self.exchange_attempts = {}
        self.state = 1
        self.req_exchange = None

        self.arbitrage_opportunities = []
        self.msg = msg

    async def get_state(self):
        match self.state:
            case 1:
                return "Инициализация алгоритма"
            case 2.1:
                return f"Получение данных от {self.req_exchange}"
            case 2.2:
                return f"Ошибка получения данных от {self.req_exchange}," \
                       f" повторный запрос...\nПопытка {self.exchange_attempts[self.req_exchange]}"
            case 3:
                return f"Анализ данных"
            case 4:
                return "Сортировка"

    async def edit_info_message(self):
        text = await self.get_state()
        if self.msg:
            try:
                await self.msg.edit_text(text=textwrap.dedent(text))
            except MessageNotModified:
                pass
        else:
            print(text)

    async def get_tickers(self, exchange, name):
        if self.exchange_attempts[exchange.id] == 4:
            return name, []
        self.req_exchange = exchange.id
        self.exchange_attempts[exchange.id] += 1
        await self.edit_info_message()

        try:
            tickers = await exchange.fetch_tickers()
        except RequestTimeout:
            self.state = 2.2
            return await self.get_tickers(exchange, name)
        finally:
            self.exchange_attempts[exchange.id] = 0
            await exchange.close()

        self.exchange_attempts[exchange.id] = 0
        return name, tickers

    async def get_markets(self, exchange):
        if self.exchange_attempts[exchange.id] == 4:
            return []
        self.req_exchange = exchange.id
        self.exchange_attempts[exchange.id] += 1
        await self.edit_info_message()

        try:
            markets = await exchange.load_markets()
        except RequestTimeout:
            self.state = 2.2
            return await self.get_markets(exchange)
        finally:
            self.exchange_attempts[exchange.id] = 0
            await exchange.close()

        self.exchange_attempts[exchange.id] = 0
        return markets

    async def verify_all_pairs(self, exchange_names):
        for pair in self.arbitrage_opportunities:
            symbol = pair['symbol']
            indexes = [
                exchange_names.index(pair["buy_exchange"]),
                exchange_names.index(pair["sell_exchange"])
            ]
            markets = [
                self.markets[indexes[0]][symbol],
                self.markets[indexes[1]][symbol]
            ]
            if 'contractAddress' in markets[0] and 'contractAddress' in markets[1]:
                print(markets[0]['contractAddress'], markets[1]['contractAddress'])
                pair['verified'] = markets[0]['contractAddress'] == markets[1]['contractAddress']
            else:
                print(f"Not found contract addresses for {symbol}")
                pair['verified'] = False

    async def get_arbitrage(self, exchange_names, chosen_percents):
        self.arbitrage_opportunities.clear()
        exchanges = [getattr(ccxt, exchange_name)() for exchange_name in exchange_names]
        self.exchange_attempts = {exchange_name: 0 for exchange_name in exchange_names}
        self.state = 2.1
        self.markets = await asyncio.gather(
            *[self.get_markets(exchange) for exchange in exchanges]
        )
        self.tickers: list[dict] = await asyncio.gather(
            *[self.get_tickers(exchange, name) for exchange, name in zip(exchanges, exchange_names)]
        )

        for ticker in self.tickers:
            exchange_name = ticker[0]
            for dict_pair_symbol, dict_pair in ticker[-1].items():
                if dict_pair.get('askVolume') and dict_pair.get('bidVolume'):
                    pair = Pair(dict_pair_symbol, exchange_name, dict_pair["bid"], dict_pair["ask"])
                    self.pair_list.append(pair)

        self.state = 3
        await asyncio.gather(*[exchange.close() for exchange in exchanges])

        self.arbitrage_opportunities = self.pair_list.get_arbitrage()
        return self.arbitrage_opportunities


if __name__ == '__main__':
    test = CcxtAPI()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test.get_arbitrage(
        ["binance", "huobipro", "kucoin", "bybit", "gate", "mexc"],
        "0.9-3"
    ))
