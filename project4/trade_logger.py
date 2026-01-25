import os
import sqlite3
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

class FixedTradeLogger:
    def __init__(self, db_path=None):
        """
        Initialize trade logger with automatic path resolution
        
        Args:
            db_path: Database path. If None, uses intelligent defaults
        """
        # Determine the best database path
        if db_path is None:
            db_path = self.get_best_db_path()
        
        self.db_path = db_path
        self.conn = None
        self.initialize_database()
    
    def get_best_db_path(self):
        """Get the best database path that works"""
        possible_paths = [
            # 1. Same directory as script (most reliable)
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trades.db'),
            
            # 2. Current working directory
            os.path.join(os.getcwd(), 'trades.db'),
            
            # 3. In data folder
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'trades.db'),
            
            # 4. User's home directory (always writable)
            os.path.join(os.path.expanduser('~'), 'forex_bot_trades.db'),
            
            # 5. Temp directory
            os.path.join(os.environ.get('TEMP', '/tmp'), 'trades.db'),
        ]
        
        # Try each path
        for path in possible_paths:
            try:
                # Create parent directory if needed
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                
                # Test if we can create/write to this location
                test_conn = sqlite3.connect(path)
                test_conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER)")
                test_conn.execute("DROP TABLE test")
                test_conn.close()
                
                print(f"✅ Using database at: {path}")
                return path
                
            except Exception as e:
                continue
        
        # If all else fails, use in-memory database
        print("⚠️ Could not find writable path, using in-memory database")
        return ':memory:'
    
    def initialize_database(self):
        """Initialize database connection and tables"""
        try:
            # Create parent directory if using file-based database
            if self.db_path != ':memory:':
                Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            
            # Create tables
            self.create_tables()
            
            # Also create JSON backup file
            self.ensure_json_backup()
            
            print(f"📊 Database initialized: {self.db_path}")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            print("💡 Falling back to JSON-only logging")
            self.conn = None
            self.db_path = None
    
    def create_tables(self):
        """Create database tables"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ticket INTEGER,
                type TEXT CHECK(type IN ('BUY', 'SELL')),
                symbol TEXT,
                lots REAL,
                entry_price REAL,
                exit_price REAL,
                sl REAL,
                tp REAL,
                profit REAL DEFAULT 0,
                strategy TEXT,
                reason TEXT,
                balance REAL,
                status TEXT DEFAULT 'OPEN' CHECK(status IN ('OPEN', 'CLOSED', 'PENDING')),
                close_time DATETIME,
                close_reason TEXT
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)')
        
        # Market data table (for analysis)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                symbol TEXT,
                bid REAL,
                ask REAL,
                spread REAL,
                rsi REAL,
                sma_20 REAL,
                sma_50 REAL,
                ema_12 REAL,
                ema_26 REAL,
                bb_upper REAL,
                bb_lower REAL,
                volume REAL
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_profit REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def ensure_json_backup(self):
        """Ensure JSON backup file exists"""
        json_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            'trades_backup.json'
        )
        
        # Create empty JSON array if file doesn't exist
        if not os.path.exists(json_path):
            with open(json_path, 'w') as f:
                json.dump([], f)
    
    def log_trade(self, trade_data):
        """
        Log trade to both database and JSON backup
        
        Args:
            trade_data: Dictionary containing trade information
        """
        # Always log to JSON backup (more reliable)
        self.log_to_json(trade_data)
        
        # Log to database if available
        if self.conn:
            try:
                cursor = self.conn.cursor()
                
                cursor.execute('''
                    INSERT INTO trades 
                    (ticket, type, symbol, lots, entry_price, sl, tp, 
                     strategy, reason, balance, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade_data.get('ticket'),
                    trade_data.get('type'),
                    trade_data.get('symbol'),
                    trade_data.get('lots'),
                    trade_data.get('entry_price'),
                    trade_data.get('sl'),
                    trade_data.get('tp'),
                    trade_data.get('strategy'),
                    trade_data.get('reason'),
                    trade_data.get('balance'),
                    trade_data.get('status', 'OPEN')
                ))
                
                self.conn.commit()
                
                # Update performance metrics
                self.update_performance_metrics()
                
            except Exception as e:
                print(f"⚠️ Database logging failed: {e}")
                print("💡 Trade was saved to JSON backup")
    
    def log_to_json(self, trade_data):
        """Log trade to JSON file"""
        try:
            json_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                'trades_backup.json'
            )
            
            # Read existing data
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    try:
                        existing_data = json.load(f)
                    except:
                        existing_data = []
            else:
                existing_data = []
            
            # Add timestamp if not present
            if 'timestamp' not in trade_data:
                trade_data['timestamp'] = datetime.now().isoformat()
            
            # Add new trade
            existing_data.append(trade_data)
            
            # Write back
            with open(json_path, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ JSON logging failed: {e}")
            # Last resort: append to simple text file
            try:
                with open('trades_simple.log', 'a') as f:
                    f.write(f"{datetime.now()}: {trade_data}\n")
            except:
                pass
    
    def update_performance_metrics(self):
        """Update daily performance metrics"""
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate today's metrics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN profit > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN profit < 0 THEN 1 ELSE 0 END) as losing_trades,
                    COALESCE(SUM(profit), 0) as total_profit
                FROM trades 
                WHERE DATE(timestamp) = DATE(?)
            ''', (today,))
            
            result = cursor.fetchone()
            
            if result:
                total_trades = result[0] or 0
                winning_trades = result[1] or 0
                losing_trades = result[2] or 0
                total_profit = result[3] or 0
                
                win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
                
                # Insert or update performance record
                cursor.execute('''
                    INSERT OR REPLACE INTO performance 
                    (date, total_trades, winning_trades, losing_trades, total_profit, win_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (today, total_trades, winning_trades, losing_trades, total_profit, win_rate))
                
                self.conn.commit()
                
        except Exception as e:
            print(f"⚠️ Performance update failed: {e}")
    
    def get_trade_history(self, days=30, symbol=None):
        """Get trade history as DataFrame"""
        try:
            # Try database first
            if self.conn:
                query = "SELECT * FROM trades WHERE timestamp >= datetime('now', '-? days')"
                params = [days]
                
                if symbol:
                    query += " AND symbol = ?"
                    params.append(symbol)
                
                query += " ORDER BY timestamp DESC"
                
                df = pd.read_sql_query(query, self.conn, params=params)
                
                if not df.empty:
                    return df
            
            # Fallback to JSON
            json_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                'trades_backup.json'
            )
            
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.load(f)
                
                if data:
                    df = pd.DataFrame(data)
                    
                    # Filter by date
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    cutoff_date = datetime.now() - pd.Timedelta(days=days)
                    df = df[df['timestamp'] >= cutoff_date]
                    
                    # Filter by symbol if specified
                    if symbol and 'symbol' in df.columns:
                        df = df[df['symbol'] == symbol]
                    
                    return df
                    
        except Exception as e:
            print(f"⚠️ Could not load trade history: {e}")
        
        return pd.DataFrame()
    
    def calculate_statistics(self, days=30):
        """Calculate trading statistics"""
        df = self.get_trade_history(days)
        
        if df.empty:
            return {}
        
        try:
            total_trades = len(df)
            winning_trades = len(df[df['profit'] > 0]) if 'profit' in df.columns else 0
            losing_trades = len(df[df['profit'] < 0]) if 'profit' in df.columns else 0
            
            total_profit = df['profit'].sum() if 'profit' in df.columns else 0
            avg_win = df[df['profit'] > 0]['profit'].mean() if winning_trades > 0 else 0
            avg_loss = df[df['profit'] < 0]['profit'].mean() if losing_trades > 0 else 0
            
            profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 else float('inf')
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_profit': total_profit,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'largest_win': df['profit'].max() if 'profit' in df.columns else 0,
                'largest_loss': df['profit'].min() if 'profit' in df.columns else 0,
                'period_days': days
            }
            
        except Exception as e:
            print(f"⚠️ Statistics calculation failed: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

# Singleton instance for easy import
logger_instance = None

def get_logger():
    """Get or create logger instance"""
    global logger_instance
    if logger_instance is None:
        logger_instance = FixedTradeLogger()
    return logger_instance

# Quick test function
def test_logger():
    """Test the logger"""
    logger = FixedTradeLogger()
    
    # Test trade data
    test_trade = {
        'ticket': 123456,
        'type': 'BUY',
        'symbol': 'USDTUGX',
        'lots': 0.01,
        'entry_price': 3800.50,
        'sl': 3770.50,
        'tp': 3830.50,
        'strategy': 'MA_Crossover',
        'reason': 'Golden Cross detected',
        'balance': 1000.00,
        'status': 'OPEN'
    }
    
    # Log test trade
    logger.log_trade(test_trade)
    
    # Get statistics
    stats = logger.calculate_statistics()
    print("📊 Statistics:", stats)
    
    # Close
    logger.close()
    
    return "✅ Logger test completed"

if __name__ == '__main__':
    test_logger()