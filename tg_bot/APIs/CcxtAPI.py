import asyncio

import ccxt.async_support as ccxt

async def get_tickers(exchange):
    try:
        tickers = await exchange.fetch_tickers()
    except Exception as e:
        print(f"Ошибка загрузки информации по {exchange.id}, повторный запрос...")
        return await get_tickers(exchange)
    finally:
        await exchange.close()
    return tickers


async def get_markets(exchange):
    try:
        markets = await exchange.load_markets()
    except Exception as e:
        print(f"Ошибка загрузки информации по '{exchange.id}', повторный запрос...")
        return await get_markets(exchange)
    finally:
        await exchange.close()
    return markets


async def get_arbitrage(exchange_names):
    arbitrage_opportunities = {
        "0.9-3": [],
        "3-5": [],
        "5-8": [],
        "8+": []
    }
    print(exchange_names)
    exchanges = [getattr(ccxt, exchange_name)() for exchange_name in exchange_names]
    tickers = await asyncio.gather(*[get_tickers(exchange) for exchange in exchanges])

    for symbol, ticker in tickers[0].items():
        if any(symbol in exchange_tickers for exchange_tickers in tickers):
            for i in range(len(exchange_names)):
                for j in range(i + 1, len(exchange_names)):
                    if symbol in tickers[i] and symbol in tickers[j]:
                        ask_i = tickers[i][symbol]['ask']  # Покупка
                        bid_j = tickers[j][symbol]['bid']  # Продажа
                        if ask_i and bid_j and ask_i != 0 and ask_i < bid_j:
                            if tickers[i][symbol].get('askVolume') and tickers[j][symbol].get('bidVolume'):
                                opportunity = (bid_j / ask_i - 1) * 100
                                if opportunity > 0 and \
                                        tickers[i][symbol]['askVolume'] and tickers[j][symbol]['bidVolume']:
                                    symbol_arbitrage = {
                                        'symbol': symbol,
                                        'buy_exchange': exchange_names[i],
                                        'sell_exchange': exchange_names[j],
                                        'opportunity': opportunity,
                                        'buy_volume': tickers[i][symbol]['askVolume'],
                                        'sell_volume': tickers[j][symbol]['bidVolume']
                                    }
                                    if opportunity >= 8:
                                        arbitrage_opportunities["8+"].append(symbol_arbitrage)
                                    elif opportunity >= 5:
                                        arbitrage_opportunities["5-8"].append(symbol_arbitrage)
                                    elif opportunity >= 3:
                                        arbitrage_opportunities["3-5"].append(symbol_arbitrage)
                                    elif opportunity >= 0.9:
                                        arbitrage_opportunities["0.9-3"].append(symbol_arbitrage)

    arbitrage_opportunities = {
        k: sorted(v, reverse=True, key=lambda x: x['opportunity']) for k, v in arbitrage_opportunities.items()
    }

    await asyncio.gather(*[exchange.close() for exchange in exchanges])
    return arbitrage_opportunities


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_arbitrage(["binance", "huobipro", "kucoin", "bybit", "gate", "mexc"]))
