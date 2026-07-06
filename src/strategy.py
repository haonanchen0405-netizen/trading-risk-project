import pandas as pd 

def calculate_momentum(prices,lookback = 60):
    momentum = prices/prices.shift(lookback) - 1
    return momentum

def generate_signal(prices, lookback = 60):
    momentum = calculate_momentum(prices, lookback)
    signal = (momentum > 0).astype(int)
    return signal

def generate_position(signal):
    position = signal.shift(1)
    return position