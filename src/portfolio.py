import pandas as pd 

def calculate_equal_weights(position):
    active_count = position.sum(axis = 1)
    raw_weights = position.div(active_count,axis=0)
    weights = raw_weights.fillna(0.0)
    return weights
    

def calculate_strategy_returns(weights, returns):
    strategy_returns = (weights * returns).sum(axis=1)
    return strategy_returns