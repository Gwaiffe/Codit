#!/usr/bin/env python3
"""
FIXED FOREX BOT - With Symbol Validation
"""
import asyncio
import json
import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import ta
import os

# ============== CONFIGURATION ==============
MT5_LOGIN = '298001984'  # ADD YOUR LOGIN
MT5_PASSWORD = 'Gwaiffe@2004'  # ADD YOUR PASSWORD
MT5_SERVER = 'Exness-MT5Trial7'  # Or 'Exness-MT5Trial7'

# Try these symbols in order (first one that works will be used)
SYMBOL_CANDIDATES = [
    "EURUSD",      # Most reliable for demo accounts
    "GBPUSD",      # Second most popular
    "XAUUSD",      # Gold (often available)
    "USDJPY",      # Major pair
    "BTCUSD",      # Bitcoin (if available)
    "ETHUSD",      # Ethereum (if available)
    "USDTUGX",     # Original choice
]

# Default to first symbol, will be updated
SYMBOL = "USDTUGX"  # Default fallback

# Other settings
TIMEFRAME = 'M1'
LOT_SIZE = 0.01
RISK_PER_TRADE = 0.02
MAX_TRADES_PER_DAY = 5

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ForexBotWithSymbolFix:
    def __init__(self):
        self.trade_count_today = 0
        self.selected_symbol = None
        self.is_trading_allowed = True

    def find_working_symbol(self):
        """Find a symbol that works with the current account"""
        print("\n" + "=" * 60)
        print("SEARCHING FOR WORKING SYMBOL")
        print("=" * 60)

        for symbol in SYMBOL_CANDIDATES:
            print(f"\nTrying symbol: {symbol}")

            # Check if symbol exists
            symbol_info = mt5.symbol_info(symbol)

            if symbol_info is None:
                print(f"  ❌ {symbol} not found")
                continue

            print(f"  ✅ {symbol} found: {symbol_info.description}")

            # Try to enable if not visible
            if not symbol_info.visible:
                print(f"  ⚠️ {symbol} not visible, trying to enable...")
                enabled = mt5.symbol_select(symbol, True)
                if not enabled:
                    print(f"  ❌ Failed to enable {symbol}")
                    continue

            # Try to get a tick (actual price)
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                print(f"  ❌ Cannot get price for {symbol}")
                continue

            print(
                f"  ✅ Price available: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}")
            print(f"  📏 Spread: {(tick.ask - tick.bid):.5f}")

            self.selected_symbol = symbol
            print(f"\n🎯 SELECTED SYMBOL: {symbol}")
            return symbol

        print("\n❌ No working symbols found!")
        print("Please check:")
        print("1. Are you logged into a DEMO account?")
        print("2. Try different server: 'Exness-MT5Trial7'")
        print("3. Contact Exness support for available symbols")
        return None

    def initialize_mt5(self):
        """Initialize MT5 and find working symbol"""
        try:
            if not mt5.initialize():
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False

            # Try to login (credentials might be in terminal already)
            login = int(MT5_LOGIN) if MT5_LOGIN and MT5_LOGIN.isdigit() else 0

            if MT5_PASSWORD:  # Only login if credentials provided
                authorized = mt5.login(
                    login=login,
                    password=MT5_PASSWORD,
                    server=MT5_SERVER
                )

                if not authorized:
                    logger.error(f"MT5 login failed: {mt5.last_error()}")
                    print("⚠️ Login failed, but continuing if already logged in MT5...")

            # Get account info
            account_info = mt5.account_info()
            if account_info:
                print(f"""
                ====================================
                MT5 CONNECTED
                Account: {account_info.login}
                Server: {account_info.server}
                Balance: ${account_info.balance:.2f}
                ====================================
                """)
            else:
                print("""
                ====================================
                MT5 CONNECTED (No account info)
                Make sure you're logged in MT5 terminal!
                ====================================
                """)

            # Find working symbol
            symbol = self.find_working_symbol()
            if not symbol:
                mt5.shutdown()
                return False

            self.selected_symbol = symbol
            return True

        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False

    def get_market_data(self, periods: int = 100):
        """Get market data for selected symbol"""
        if not self.selected_symbol:
            logger.error("No symbol selected!")
            return None

        try:
            tick = mt5.symbol_info_tick(self.selected_symbol)
            if tick is None:
                logger.error(f"Cannot get tick for {self.selected_symbol}")
                return None

            # Get historical data
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }

            timeframe = timeframe_map.get(TIMEFRAME, mt5.TIMEFRAME_M1)
            rates = mt5.copy_rates_from_pos(
                self.selected_symbol, timeframe, 0, periods)

            if rates is None:
                logger.warning(
                    f"Cannot get historical data for {self.selected_symbol}")
                # Return at least current tick
                return {
                    'tick': tick,
                    'current_price': tick.ask,
                    'bid': tick.bid,
                    'ask': tick.ask,
                    'spread': tick.ask - tick.bid,
                    'time': datetime.now(),
                    'symbol': self.selected_symbol
                }

            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')

            # Add simple indicators
            if len(df) > 20:
                df['SMA_20'] = df['close'].rolling(window=20).mean()
                df['SMA_50'] = df['close'].rolling(window=50).mean()
                df['RSI'] = self.calculate_rsi(df['close'])

            return {
                'tick': tick,
                'df': df,
                'current_price': tick.ask,
                'bid': tick.bid,
                'ask': tick.ask,
                'spread': tick.ask - tick.bid,
                'time': datetime.now(),
                'symbol': self.selected_symbol
            }

        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def simple_trading_logic(self, market_data):
        """Simple moving average crossover strategy"""
        if not market_data or 'df' not in market_data:
            return None

        df = market_data['df']
        current_price = market_data['current_price']

        if len(df) < 50:
            return None

        # Check if we have necessary indicators
        if 'SMA_20' not in df.columns or 'SMA_50' not in df.columns:
            return None

        sma_20 = df['SMA_20'].iloc[-1]
        sma_50 = df['SMA_50'].iloc[-1]
        sma_20_prev = df['SMA_20'].iloc[-2] if len(df) > 1 else sma_20
        sma_50_prev = df['SMA_50'].iloc[-2] if len(df) > 1 else sma_50

        signal = None
        reason = ""

        # Golden Cross
        if sma_20 > sma_50 and sma_20_prev <= sma_50_prev:
            signal = 'BUY'
            reason = f"Golden Cross (SMA20 > SMA50)"

        # Death Cross
        elif sma_20 < sma_50 and sma_20_prev >= sma_50_prev:
            signal = 'SELL'
            reason = f"Death Cross (SMA20 < SMA50)"

        if signal:
            # Simple stop loss and take profit
            if signal == 'BUY':
                stop_loss = current_price * 0.995
                take_profit = current_price * 1.01
            else:
                stop_loss = current_price * 1.005
                take_profit = current_price * 0.99

            return {
                'signal': signal,
                'reason': reason,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': 0.7
            }

        return None

    async def trading_loop(self):
        """Main trading loop"""
        print("\n" + "=" * 60)
        print("FOREX BOT STARTED")
        print(f"Trading: {self.selected_symbol}")
        print("=" * 60)

        while True:
            try:
                # Get market data
                market_data = self.get_market_data()

                if market_data:
                    # Display price
                    tick = market_data['tick']
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"{self.selected_symbol}: "
                          f"Bid={tick.bid:.5f}, Ask={tick.ask:.5f}, "
                          f"Spread={(tick.ask - tick.bid):.5f}")

                    # Simple trading logic
                    if self.trade_count_today < MAX_TRADES_PER_DAY:
                        signal = self.simple_trading_logic(market_data)

                        if signal and signal['confidence'] > 0.6:
                            print(
                                f"  💡 Signal: {signal['signal']} - {signal['reason']}")
                            # You can add trade execution here later

                await asyncio.sleep(10)  # Check every 10 seconds

            except KeyboardInterrupt:
                print("\nBot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                await asyncio.sleep(30)

    def shutdown(self):
        """Clean shutdown"""
        try:
            mt5.shutdown()
            print("Bot shutdown complete")
        except:
            pass

# ============== MAIN EXECUTION ==============


async def main():
    bot = ForexBotWithSymbolFix()

    if not bot.initialize_mt5():
        print("Failed to initialize. Please check:")
        print("1. Is MT5 running?")
        print("2. Are you logged into a DEMO account?")
        print("3. Try opening MT5 manually first")
        return

    try:
        await bot.trading_loop()
    finally:
        bot.shutdown()

if __name__ == '__main__':
    print("Starting Forex Bot with Symbol Fix...")
    asyncio.run(main())
