from datetime import datetime


class Pair:
    def __init__(self, symbol: str, exchange: str, bid: float, ask: float):
        self.symbol = symbol
        self.base_symbol = symbol.split("/")[0]
        self.quote_symbol = symbol.split("/")[-1]
        self.exchange = exchange
        self.bid = bid
        self.ask = ask

    def get_base_symbol(self):
        return self.base_symbol

    def get_quote_symbol(self):
        return self.quote_symbol

    def __str__(self):
        return self.symbol


class PairList:

    def __init__(self):
        self.pair_list: list[Pair] = []
        self.compared_pairs: dict[str, list[Pair]] = {}
        self.arbitrage_opportunities: dict[str, list] = {}

    def append(self, pair: Pair):
        self.pair_list.append(pair)

    def extend(self, pairs: list[Pair]):
        self.pair_list.extend(pairs)

    def get_arbitrage(self):
        if self.arbitrage_opportunities:
            return self.arbitrage_opportunities
        self.arbitrage_opportunities = {
            "8+": [],
            "5-8": [],
            "3-5": [],
            "0.9-3": []
        }

        if not self.compared_pairs:
            self.compared_pairs = self.get_compared_pairs()

        for symbol, pairs in self.compared_pairs.items():
            if len(pairs) > 1:
                min_ask_pair = min(pairs, key=lambda x: x.ask)
                max_bid_pair = max(pairs, key=lambda x: x.bid)
                min_ask = min_ask_pair.ask
                max_bid = max_bid_pair.bid
                if min_ask < max_bid:
                    opportunity = (max_bid / min_ask - 1) * 100
                    if opportunity >= 8:
                        self.arbitrage_opportunities["8+"].append({
                            "pairs": [min_ask_pair, max_bid_pair],
                            "opportunity": opportunity
                        })
                    if 5 <= opportunity < 8:
                        self.arbitrage_opportunities["5-8"].append({
                            "pairs": [min_ask_pair, max_bid_pair],
                            "opportunity": opportunity
                        })
                    if 3 <= opportunity < 5:
                        self.arbitrage_opportunities["3-5"].append({
                            "pairs": [min_ask_pair, max_bid_pair],
                            "opportunity": opportunity
                        })
                    if 0.9 <= opportunity < 3:
                        self.arbitrage_opportunities["0.9-3"].append({
                            "pairs": [min_ask_pair, max_bid_pair],
                            "opportunity": opportunity
                        })

        return self.arbitrage_opportunities

    def get_compared_pairs(self):
        if self.compared_pairs:
            return self.compared_pairs

        self.compared_pairs: dict[str, list[Pair]] = {
            pair.symbol: [other_pair for other_pair in self.pair_list if other_pair.symbol == pair.symbol]
            for pair in self.pair_list
        }
        return self.compared_pairs

    @staticmethod
    def get_percent_arbitrage_text(arbitrage_opportunities, percent):
        if not arbitrage_opportunities[percent]:
            string = "Не найдено подходящих пар"
        else:
            string = "\n".join([
                f"{arbitrage['pairs'][0].symbol}\n"
                f"{arbitrage['pairs'][0].exchange}/{arbitrage['pairs'][1].exchange}"
                f" = {'%.2f' % arbitrage['opportunity']}%\n"
                # f"{arbitrage['verified']}"
                for arbitrage in arbitrage_opportunities[percent]
            ])
        arbitrage_str = f"Актуальный арбитраж на {datetime.now().time().strftime('%H:%M')}\n" \
                        f"Процентный диапазон: {percent}%\n" \
                        f"{string}"

        return arbitrage_str
