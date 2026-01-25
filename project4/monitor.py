import asyncio
import json
import time
import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd

# ============== CONFIGURATION ==============
MT5_LOGIN = 'YOUR_DEMO_LOGIN'  # USE DEMO ACCOUNT FIRST!
MT5_PASSWORD = 'YOUR_DEMO_PASSWORD'
MT5_SERVER = 'Exness-Demo'  # Use demo server
SYMBOL = 'USDTUGX'
TIMEFRAME = mt5.TIMEFRAME_M1  # 1-minute timeframe

# RISK MANAGEMENT SETTINGS (ADJUST THESE!)
RISK_PER_TRADE = 0.02  # 2% risk per trade
MAX_TRADES_PER_DAY = 3
DAILY_LOSS_LIMIT = -0.05  # -5% daily loss limit
TAKE_PROFIT_PIPS = 100  # 100 pips profit target
STOP_LOSS_PIPS = 50     # 50 pips stop loss
LOT_SIZE = 0.01         # Start with 0.01 lots (micro lot)

class ForexTradingBot:
    def __init__(self):
        self.trade_count_today = 0
        self.daily_pnl = 0.0
        self.is_trading_allowed = True
        self.positions = []
        
    def initialize_mt5(self):
        """Initialize MT5 connection"""
        if not mt5.initialize(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
            print(f'MT5 init failed: {mt5.last_error()}')
            return False
        
        authorized = mt5.login(login=MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
        if not authorized:
            print(f'Login failed: {mt5.last_error()}')
            mt5.shutdown()
            return False
            
        print(f'Connected to {MT5_SERVER}. Account: {MT5_LOGIN}')
        print(f'Balance: ${mt5.account_info().balance:.2f}')
        return True
    
    def calculate_position_size(self, stop_loss_pips):
        """Calculate position size based on risk management"""
        account_balance = mt5.account_info().balance
        risk_amount = account_balance * RISK_PER_TRADE
        
        # Get symbol info for pip calculation
        symbol_info = mt5.symbol_info(SYMBOL)
        if not symbol_info:
            return LOT_SIZE  # Default to small size
            
        # Calculate position size based on risk
        tick_size = symbol_info.trade_tick_size
        pip_value = tick_size * 10000  # Approximate for UGX
        
        if pip_value > 0:
            lots = risk_amount / (stop_loss_pips * pip_value)
            # Cap at reasonable size
            lots = min(lots, 0.1)  # Max 0.1 lots
            return round(lots, 2)
        
        return LOT_SIZE
    
    def get_market_data(self):
        """Get current market prices and indicators"""
        try:
            # Get current tick
            tick = mt5.symbol_info_tick(SYMBOL)
            if tick is None:
                return None
            
            # Get last 100 candles for analysis
            rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 100)
            if rates is None:
                return tick, None
            
            df = pd.DataFrame(rates)
            
            # Calculate basic indicators
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            df['SMA_50'] = df['close'].rolling(window=50).mean()
            df['RSI'] = self.calculate_rsi(df['close'], 14)
            
            current_price = tick.ask
            sma_20 = df['SMA_20'].iloc[-1]
            sma_50 = df['SMA_50'].iloc[-1]
            rsi = df['RSI'].iloc[-1]
            
            return {
                'tick': tick,
                'price': current_price,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'rsi': rsi,
                'df': df
            }
            
        except Exception as e:
            print(f'Error getting market data: {e}')
            return None
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def check_trading_conditions(self, market_data):
        """Check if conditions are right for trading"""
        if not market_data or not self.is_trading_allowed:
            return None
        
        price = market_data['price']
        sma_20 = market_data['sma_20']
        sma_50 = market_data['sma_50']
        rsi = market_data['rsi']
        
        # Check daily limits
        if self.trade_count_today >= MAX_TRADES_PER_DAY:
            print(f'Daily trade limit reached: {MAX_TRADES_PER_DAY}')
            return None
        
        if self.daily_pnl <= DAILY_LOSS_LIMIT:
            print(f'Daily loss limit reached: {DAILY_LOSS_LIMIT*100}%')
            self.is_trading_allowed = False
            return None
        
        # Trading Strategy 1: Moving Average Crossover
        buy_signal = False
        sell_signal = False
        
        # BUY Signal: Price above both MAs and RSI not overbought
        if price > sma_20 > sma_50 and rsi < 70:
            buy_signal = True
            
        # SELL Signal: Price below both MAs and RSI not oversold  
        elif price < sma_20 < sma_50 and rsi > 30:
            sell_signal = True
        
        # Trading Strategy 2: RSI extremes
        if rsi < 30 and price > sma_20:  # Oversold bounce
            buy_signal = True
        elif rsi > 70 and price < sma_20:  # Overbought drop
            sell_signal = True
        
        if buy_signal:
            return 'BUY'
        elif sell_signal:
            return 'SELL'
        
        return None
    
    def place_trade(self, trade_type, market_data):
        """Execute a trade with proper risk management"""
        try:
            tick = market_data['tick']
            
            if trade_type == 'BUY':
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
                sl = price - (STOP_LOSS_PIPS * 0.0001)  # Adjust for UGX
                tp = price + (TAKE_PROFIT_PIPS * 0.0001)
            else:  # SELL
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
                sl = price + (STOP_LOSS_PIPS * 0.0001)
                tp = price - (TAKE_PROFIT_PIPS * 0.0001)
            
            # Calculate position size
            lot_size = self.calculate_position_size(STOP_LOSS_PIPS)
            
            request = {
                'action': mt5.TRADE_ACTION_DEAL,
                'symbol': SYMBOL,
                'volume': lot_size,
                'type': order_type,
                'price': price,
                'sl': sl,
                'tp': tp,
                'deviation': 10,
                'magic': 1001,
                'comment': 'AutoTradeBot',
                'type_time': mt5.ORDER_TIME_GTC,
                'type_filling': mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.trade_count_today += 1
                print(f'''
    ✓ Trade Executed: {trade_type} {lot_size} lots
    Price: {price}
    SL: {sl:.5f} | TP: {tp:.5f}
    Ticket: {result.order}
    Balance: ${mt5.account_info().balance:.2f}
                ''')
                
                # Log the trade
                self.log_trade(result, trade_type, lot_size, price, sl, tp)
                
            else:
                print(f'✗ Trade failed: {result.comment}')
                
            return result
            
        except Exception as e:
            print(f'Error placing trade: {e}')
            return None
    
    def log_trade(self, result, trade_type, lots, price, sl, tp):
        """Log trade details to file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ticket': result.order,
            'type': trade_type,
            'lots': lots,
            'price': price,
            'sl': sl,
            'tp': tp,
            'balance': mt5.account_info().balance
        }
        
        try:
            with open('trades_log.json', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except:
            pass
    
    def check_open_positions(self):
        """Check and update open positions"""
        positions = mt5.positions_get(symbol=SYMBOL)
        if positions:
            total_profit = sum(pos.profit for pos in positions)
            print(f'Open positions: {len(positions)} | P&L: ${total_profit:.2f}')
            return total_profit
        return 0
    
    def reset_daily_counts(self):
        """Reset daily counters at midnight"""
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            self.trade_count_today = 0
            self.daily_pnl = 0.0
            self.is_trading_allowed = True
            print('Daily counters reset')
    
    async def trading_loop(self):
        """Main trading loop"""
        print(f'Starting Forex Trading Bot for {SYMBOL}')
        print(f'Risk per trade: {RISK_PER_TRADE*100}%')
        print(f'Stop Loss: {STOP_LOSS_PIPS} pips | Take Profit: {TAKE_PROFIT_PIPS} pips')
        print('=' * 50)
        
        while True:
            try:
                # Reset daily counts at midnight
                self.reset_daily_counts()
                
                # Get market data
                market_data = self.get_market_data()
                if not market_data:
                    await asyncio.sleep(10)
                    continue
                
                # Display market info
                price = market_data['price']
                rsi = market_data['rsi']
                print(f'\n{datetime.now().strftime("%H:%M:%S")} | Price: {price:.5f} | RSI: {rsi:.1f} | Trades: {self.trade_count_today}/{MAX_TRADES_PER_DAY}')
                
                # Check open positions
                open_pnl = self.check_open_positions()
                self.daily_pnl = open_pnl / mt5.account_info().balance
                
                # Check trading conditions
                signal = self.check_trading_conditions(market_data)
                
                if signal:
                    print(f'Signal detected: {signal}')
                    result = self.place_trade(signal, market_data)
                    if result and result.retcode != mt5.TRADE_RETCODE_DONE:
                        print(f'Trade rejected: {result.comment}')
                
                # Wait before next check
                await asyncio.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                print('\nBot stopped by user')
                break
            except Exception as e:
                print(f'Error in main loop: {e}')
                await asyncio.sleep(30)
    
    def shutdown(self):
        """Clean shutdown"""
        mt5.shutdown()
        print('Bot shutdown complete')

# ============== MAIN EXECUTION ==============
async def main():
    bot = ForexTradingBot()
    
    if not bot.initialize_mt5():
        print('Failed to initialize MT5. Exiting.')
        return
    
    try:
        await bot.trading_loop()
    finally:
        bot.shutdown()

if __name__ == '__main__':
    # IMPORTANT: Run with demo account first!
    asyncio.run(main())