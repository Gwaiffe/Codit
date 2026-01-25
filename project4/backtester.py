import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import MetaTrader5 as mt5
from typing import Dict, List, Tuple
import logging
from config import *

logger = logging.getLogger(__name__)


class Backtester:
    def __init__(self):
        self.results = {}

    def fetch_historical_data(self, symbol: str, timeframe: str,
                              start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch historical data from MT5"""
        try:
            if not mt5.initialize():
                logger.error("MT5 initialization failed")
                return pd.DataFrame()

            # Convert timeframe
            tf_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }

            timeframe_mt5 = tf_map.get(timeframe, mt5.TIMEFRAME_M1)

            # Convert dates to timestamp
            from_date = start_date
            to_date = end_date

            # Fetch rates
            rates = mt5.copy_rates_range(
                symbol, timeframe_mt5, from_date, to_date)

            if rates is None:
                logger.error(f"No data fetched for {symbol}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)

            mt5.shutdown()
            return df

        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for backtesting"""
        # Moving Averages
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['EMA_12'] = df['close'].ewm(span=12).mean()
        df['EMA_26'] = df['close'].ewm(span=26).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()

        # Bollinger Bands
        df['BB_Middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)

        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['ATR'] = true_range.rolling(14).mean()

        return df

    def ma_crossover_backtest(self, df: pd.DataFrame, initial_balance: float = 10000) -> Dict:
        """Backtest MA Crossover strategy"""
        df = df.copy()
        df['signal'] = 0
        df['position'] = 0
        df['returns'] = 0
        df['equity'] = initial_balance

        # Generate signals
        df['signal'] = np.where(df['SMA_20'] > df['SMA_50'], 1, 0)
        df['position'] = df['signal'].diff()

        # Calculate returns
        df['returns'] = df['close'].pct_change() * df['signal'].shift(1)
        df['equity'] = initial_balance * (1 + df['returns'].cumsum())

        # Calculate metrics
        total_return = (df['equity'].iloc[-1] -
                        initial_balance) / initial_balance
        sharpe_ratio = self.calculate_sharpe_ratio(df['returns'])
        max_drawdown = self.calculate_max_drawdown(df['equity'])
        win_rate = self.calculate_win_rate(df['returns'])

        trades = len(df[df['position'] != 0]) // 2

        return {
            'strategy': 'MA_Crossover',
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': trades,
            'final_equity': df['equity'].iloc[-1]
        }

    def mean_reversion_backtest(self, df: pd.DataFrame, initial_balance: float = 10000) -> Dict:
        """Backtest Mean Reversion strategy"""
        df = df.copy()
        df['signal'] = 0
        df['position'] = 0

        # Generate signals
        df['oversold'] = (df['close'] < df['BB_Lower']) & (df['RSI'] < 30)
        df['overbought'] = (df['close'] > df['BB_Upper']) & (df['RSI'] > 70)

        df['signal'] = np.where(df['oversold'], 1,
                                np.where(df['overbought'], -1, 0))
        df['position'] = df['signal'].diff()

        # Calculate returns
        df['returns'] = df['close'].pct_change() * df['signal'].shift(1)
        df['equity'] = initial_balance * (1 + df['returns'].cumsum())

        # Calculate metrics
        total_return = (df['equity'].iloc[-1] -
                        initial_balance) / initial_balance
        sharpe_ratio = self.calculate_sharpe_ratio(df['returns'])
        max_drawdown = self.calculate_max_drawdown(df['equity'])
        win_rate = self.calculate_win_rate(df['returns'])

        trades = len(df[df['position'] != 0]) // 2

        return {
            'strategy': 'Mean_Reversion',
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': trades,
            'final_equity': df['equity'].iloc[-1]
        }

    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if returns.std() == 0:
            return 0
        excess_returns = returns - (risk_free_rate / 252)
        return np.sqrt(252) * excess_returns.mean() / returns.std()

    def calculate_max_drawdown(self, equity: pd.Series) -> float:
        """Calculate maximum drawdown"""
        rolling_max = equity.expanding().max()
        drawdown = (equity - rolling_max) / rolling_max
        return drawdown.min()

    def calculate_win_rate(self, returns: pd.Series) -> float:
        """Calculate win rate"""
        winning_trades = len(returns[returns > 0])
        total_trades = len(returns[returns != 0])
        return winning_trades / total_trades if total_trades > 0 else 0

    def run_complete_backtest(self, symbol: str, months: int = 6):
        """Run complete backtest on all strategies"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months*30)

        print(f"\n{'='*60}")
        print(f"RUNNING BACKTEST: {symbol}")
        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"{'='*60}")

        # Fetch data
        df = self.fetch_historical_data(
            symbol, TIMEFRAME, start_date, end_date)
        if df.empty:
            print("No data available for backtesting")
            return

        df = self.calculate_indicators(df)

        # Run backtests
        results = []

        # MA Crossover
        ma_result = self.ma_crossover_backtest(df)
        results.append(ma_result)

        # Mean Reversion
        mr_result = self.mean_reversion_backtest(df)
        results.append(mr_result)

        # Display results
        results_df = pd.DataFrame(results)
        print("\nBACKTEST RESULTS:")
        print(results_df.to_string(index=False))

        # Save to CSV
        results_df.to_csv(
            f'backtest_results_{symbol}_{end_date.date()}.csv', index=False)
        print(
            f"\nResults saved to: backtest_results_{symbol}_{end_date.date()}.csv")

        return results_df


# Usage
if __name__ == '__main__':
    backtester = Backtester()
    backtester.run_complete_backtest(SYMBOL, months=3)
