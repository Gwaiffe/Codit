# ============== TRADING CONFIGURATION ==============

# MT5 Connection
MT5_LOGIN = '298001984'
MT5_PASSWORD = 'Gwaiffe@2004'
MT5_SERVER = 'Exness-MT5Trial9'
SYMBOL = 'USDTUGX'

# Trading Parameters
TIMEFRAME = 'M1'  # M1, M5, M15, M30, H1, H4, D1
LOT_SIZE = 0.01
MAX_SPREAD = 20  # Max spread in pips

# Risk Management
RISK_PER_TRADE = 0.02  # 2%
MAX_TRADES_PER_DAY = 5
DAILY_LOSS_LIMIT = -0.05  # -5%
MAX_DRAWDOWN = 0.10  # 10% max drawdown

# Trading Hours (UGX/EAT time)
TRADING_HOURS = {
    'start': 8,  # 8 AM
    'end': 17    # 5 PM
}

# Strategy Parameters
STRATEGIES = {
    'ma_crossover': {
        'enabled': True,
        'fast_period': 10,
        'slow_period': 30,
        'rsi_period': 14
    },
    'mean_reversion': {
        'enabled': True,
        'bollinger_period': 20,
        'std_dev': 2,
        'rsi_oversold': 30,
        'rsi_overbought': 70
    },
    'breakout': {
        'enabled': True,
        'atr_period': 14,
        'atr_multiplier': 1.5
    }
}

# Telegram Bot Configuration
TELEGRAM_CONFIG = {
    'enabled': True,
    'bot_token': '8424745062:AAG3Unp03F17OD4EnHI8dLTNW7iw6uwfqoo',
    'chat_id': '7744129188f'
}

# Database Configuration
DB_CONFIG = {
    'enabled': True,
    'path': 'data/trades.db'
}

# Performance Targets
PERFORMANCE_TARGETS = {
    'min_win_rate': 0.45,  # 45% minimum
    'min_profit_factor': 1.5,
    'max_consecutive_losses': 3
}