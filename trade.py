#!/usr/bin/python3
# -*- coding: iso-8859-1 -*-
# """ Python scalping bot for Crypto Trader games """
# __version__ = "1.0"

import sys

MaxBtcPrice = 0
BuyPrice = 0
isTpTrigerred = False
isSlTrigerred = False
PriceWhenSlTrigerred = 0
prices = []

class Bot:
    def __init__(self):
        self.botState = BotState()

    def run(self):
        while True:
            reading = input()
            print(f'reading: {reading}', file=sys.stderr, flush=True)
            if len(reading) == 0:
                continue
            self.parse(reading)

    def parse(self, info: str):
        tmp = info.split(" ")
        if tmp[0] == "settings":
            self.botState.update_settings(tmp[1], tmp[2])
        if tmp[0] == "update":
            if tmp[1] == "game":
                self.botState.update_game(tmp[2], tmp[3])
        if tmp[0] == "action":
            dollars = self.botState.stacks["USDT"] # Amount of dollars I have
            current_closing_price = self.botState.charts["USDT_BTC"].closes[-1] # Current price of BTC
            btc = self.botState.stacks["BTC"] # Amount of BTC I have
            transaction_fee = self.botState.transactionFee
            take_profit = 1.05
            stop_loss = 0.90

            print(f'My stacks are {dollars} USDT and {btc} BTC. Current closing price: {current_closing_price}', file=sys.stderr)
            trading_bot(current_closing_price, dollars, btc, stop_loss, take_profit, transaction_fee)

def calculate_sma(prices, window):
    if len(prices) < window:
        return sum(prices) / len(prices)
    return sum(prices[-window:]) / window 
 
def calculate_ema(prices, window):
    if len(prices) < window:
        return calculate_sma(prices, window)
    ema = calculate_sma(prices[:window], window)
    multiplier = 2 / (window + 1)
    for price in prices[window:]:
        ema = (price - ema) * multiplier + ema
    return ema

def calculate_rsi(prices, window=14):
    if len(prices) < window:
        return 50

    gains = 0
    losses = 0

    for i in range(1, window):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains += change
        else:
            losses -= change

    if losses == 0:
        return 100

    avg_gain = gains / window
    avg_loss = losses / window
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    for i in range(window, len(prices)):
        change = prices[i] - prices[i - 1]
        gain = max(0, change)
        loss = max(0, -change)

        avg_gain = (avg_gain * (window - 1) + gain) / window
        avg_loss = (avg_loss * (window - 1) + loss) / window

        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_bollinger_bands(prices, window=20, num_std_dev=2):
    if len(prices) < window:
        sma = sum(prices) / len(prices)
    else:
        sma = sum(prices[-window:]) / window
    variance = sum((p - sma) ** 2 for p in prices[-window:]) / window
    std_dev = variance ** 0.5
    upper_band = sma + (num_std_dev * std_dev)
    lower_band = sma - (num_std_dev * std_dev)
    return sma, upper_band, lower_band

def calculate_buying_indicator_values(sma_short, sma_long, rsi, sma, upper_band, lower_band, current_price):
    total = 0
    if sma_short > sma_long:
        total += 1
    if rsi <= 40:
        total += 1
    if current_price < lower_band:
        total += 1
    if total >= 1:
        return True
    return False

def calculate_selling_indicator_values(sma_short, sma_long, rsi, sma, upper_band, lower_band, current_price):
    total = 0
    if sma_short < sma_long:
        total += 1
    if rsi >= 70:
        total += 1
    if current_price > upper_band:
        total += 1
    if total >= 1:
        return True
    return False

def isSlreturn(current_price):
    global PriceWhenSlTrigerred

    if current_price * 1.7 < PriceWhenSlTrigerred:
        return True
    if current_price < PriceWhenSlTrigerred * 1.14:
        return False
    return True


def trading_bot(current_closing_price: float, dollars: float, btc: float, stop_loss: float, take_profit: float, transaction_fee: float):
    global MaxBtcPrice
    global BuyPrice
    global isTpTrigerred
    global isSlTrigerred
    global PriceWhenSlTrigerred
    global prices

    prices.append(current_closing_price)

    if current_closing_price > MaxBtcPrice:
        MaxBtcPrice = current_closing_price

    sma_short = calculate_sma(prices, 5)
    sma_long = calculate_sma(prices, 20)
    rsi = calculate_rsi(prices)
    sma, upper_band, lower_band = calculate_bollinger_bands(prices)

    target_buy_price = MaxBtcPrice * stop_loss
    target_sell_price = BuyPrice * take_profit

    print(f'rsi: {rsi}, sma_short: {sma_short}, sma_long: {sma_long}, upper_band: {upper_band}, lower_band: {lower_band}', file=sys.stderr)

    if take_profit is not None and stop_loss is not None:
        if dollars > 100 and sma_short > sma_long and isSlreturn(current_closing_price):
            amount_to_buy = dollars / current_closing_price
            print(f'buy USDT_BTC {amount_to_buy}', flush=True)
            print('Action: BUY', file=sys.stderr)
            BuyPrice = current_closing_price
            isSlTrigerred = False
            return
        if btc > 0 and current_closing_price < BuyPrice * stop_loss:
            print(f'sell USDT_BTC {btc}', flush=True)
            print('Action: SELL, SL TRIGERRED', file=sys.stderr)
            isSlTrigerred = True
            PriceWhenSlTrigerred = current_closing_price
            return
        if btc > 0 and sma_short < sma_long and current_closing_price > BuyPrice * take_profit:
            print(f'sell USDT_BTC {btc}', flush=True)
            print('Action: SELL, TP TRIGERRED', file=sys.stderr)
            isTpTrigerred = True
            return

        print("no_moves", flush=True)
        print('Action: NO MOVE', file=sys.stderr)

class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        for (i, key) in enumerate(format):
            value = tmp[i]
            if key == "pair":
                self.pair = value
            if key == "date":
                self.date = int(value)
            if key == "high":
                self.high = float(value)
            if key == "low":
                self.low = float(value)
            if key == "open":
                self.open = float(value)
            if key == "close":
                self.close = float(value)
            if key == "volume":
                self.volume = float(value)

    def __repr__(self):
        return str(self.pair) + str(self.date) + str(self.close) + str(self.volume)

class Chart:
    def __init__(self):
        self.dates = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []
        self.indicators = {}

    def add_candle(self, candle: Candle):
        self.dates.append(candle.date)
        self.opens.append(candle.open)
        self.highs.append(candle.high)
        self.lows.append(candle.low)
        self.closes.append(candle.close)
        self.volumes.append(candle.volume)

class BotState:
    def __init__(self):
        self.timeBank = 0
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleInterval = 1
        self.candleFormat = []
        self.candlesTotal = 0
        self.candlesGiven = 0
        self.initialStack = 0
        self.transactionFee = 0.1
        self.date = 0
        self.stacks = dict()
        self.charts = dict()

    def update_chart(self, pair: str, new_candle_str: str):
        if not (pair in self.charts):
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "timebank":
            self.maxTimeBank = int(value)
            self.timeBank = int(value)
        if key == "time_per_move":
            self.timePerMove = int(value)
        if key == "candle_interval":
            self.candleInterval = int(value)
        if key == "candle_format":
            self.candleFormat = value.split(",")
        if key == "candles_total":
            self.candlesTotal = int(value)
        if key == "candles_given":
            self.candlesGiven = int(value)
        if key == "initial_stack":
            self.initialStack = int(value)
        if key == "transaction_fee_percent":
            self.transactionFee = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        if key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))

if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
