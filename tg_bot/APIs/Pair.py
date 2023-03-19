class Pair:
    def __init__(self, base_symbol: str, quote_symbol: str):
        self.exchange_symbols: str
        self.base_symbol: str = base_symbol
        self.quote_symbol: str = quote_symbol
        self.exchanges = {"buy": '', "sell": ''}
        self.arbitrage: float

        self.buy_prices: list[float]
        self.sell_prices: list[float]

    def __str__(self):
        return f"{self.base_symbol}/{self.quote_symbol}"


