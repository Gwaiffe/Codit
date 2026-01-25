#!/usr/bin/env python3
"""
FIX SQLite3 Database Error Script
Run this BEFORE running your bot
"""
import os
import sys
import sqlite3
from pathlib import Path

def fix_database_error():
    print("🔧 Fixing SQLite3 Database Error...")
    print("=" * 60)
    
    # Create necessary directories
    directories_to_create = [
        'data',
        'logs',
        'backups',
        'exports'
    ]
    
    for directory in directories_to_create:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"⚠️ Could not create {directory}: {e}")
    
    # Create database in a safe location
    database_paths = [
        'trades.db',  # Current directory (most reliable)
        'data/trades.db',  # In data folder
        os.path.join(os.path.expanduser('~'), 'forex_bot_trades.db'),  # Home directory
        os.path.join(os.getcwd(), 'trades.db'),  # Absolute path
    ]
    
    successful_path = None
    
    for db_path in database_paths:
        try:
            print(f"\n🔍 Trying to create database at: {db_path}")
            
            # Create parent directories if needed
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Test database creation
            conn = sqlite3.connect(db_path)
            
            # Create tables
            cursor = conn.cursor()
            
            # Trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ticket INTEGER,
                    type TEXT,
                    symbol TEXT,
                    lots REAL,
                    entry_price REAL,
                    exit_price REAL,
                    sl REAL,
                    tp REAL,
                    profit REAL,
                    strategy TEXT,
                    reason TEXT,
                    balance REAL,
                    status TEXT DEFAULT 'OPEN'
                )
            ''')
            
            # Market data table
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
                    volume REAL
                )
            ''')
            
            # Performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    losing_trades INTEGER,
                    total_profit REAL,
                    max_drawdown REAL,
                    win_rate REAL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            print(f"✅ Successfully created database at: {db_path}")
            
            # Check permissions
            if os.access(db_path, os.W_OK):
                print(f"✅ Write permission granted for: {db_path}")
                successful_path = db_path
                break
            else:
                print(f"⚠️ No write permission for: {db_path}")
                
        except Exception as e:
            print(f"❌ Failed to create at {db_path}: {e}")
    
    if successful_path:
        print(f"\n🎉 Database ready at: {successful_path}")
        
        # Create a config file with the working path
        config_content = f'''# Database Configuration
import os

DB_CONFIG = {{
    'enabled': True,
    'path': r'{os.path.abspath(successful_path)}'
}}

# Alternative simpler config
SIMPLE_DB_CONFIG = {{
    'enabled': True,
    'path': 'trades.db'  # Use this if above doesn't work
}}
'''
        
        with open('database_config.py', 'w') as f:
            f.write(config_content)
        
        print("📁 Created database_config.py with working settings")
        
        return successful_path
    else:
        print("\n❌ Could not create database in any location")
        print("   Trying alternative approach...")
        
        # Use in-memory database as fallback
        print("💡 Using in-memory database (data will be lost when bot stops)")
        
        fallback_config = '''# Fallback Database Configuration
DB_CONFIG = {
    'enabled': True,
    'path': ':memory:'  # In-memory database
}
'''
        
        with open('database_config.py', 'w') as f:
            f.write(fallback_config)
        
        print("📁 Created database_config.py with in-memory settings")
        return ':memory:'

def check_permissions():
    """Check file system permissions"""
    print("\n🔐 Checking File Permissions...")
    print("=" * 60)
    
    current_dir = os.getcwd()
    print(f"Current Directory: {current_dir}")
    
    # Check write permissions
    test_file = os.path.join(current_dir, 'test_write.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ Can write to current directory")
    except Exception as e:
        print(f"❌ Cannot write to current directory: {e}")
    
    # Check if running as admin/root
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            print(f"Admin privileges: {'✅ Yes' if is_admin else '❌ No'}")
        except:
            print("⚠️ Could not check admin privileges")
    else:  # Linux/Mac
        is_root = os.geteuid() == 0
        print(f"Root privileges: {'✅ Yes' if is_root else '❌ No'}")
    
    # Suggest solutions
    print("\n💡 If you have permission issues:")
    print("1. Run terminal/IDE as Administrator (Right-click → Run as Admin)")
    print("2. Move bot to a folder you own (like Documents)")
    print("3. Use: DB_CONFIG['path'] = ':memory:' for temporary fix")

def create_simple_bot_without_database():
    """Create a bot version that doesn't use database"""
    print("\n🔄 Creating Simple Bot Without Database...")
    
    simple_bot = '''#!/usr/bin/env python3
"""
SIMPLE FOREX BOT - No Database Required
"""
import asyncio
import json
import MetaTrader5 as mt5
from datetime import datetime

# Configuration
MT5_LOGIN = ''  # Add your login
MT5_PASSWORD = ''  # Add your password
MT5_SERVER = 'Exness-Demo'  # Change if needed
SYMBOL = 'USDTUGX'

class SimpleForexBot:
    def __init__(self):
        self.trade_log = []
        self.use_json_logging = True
    
    def initialize_mt5(self):
        """Initialize MT5 without database"""
        if not mt5.initialize():
            print(f"MT5 init failed: {mt5.last_error()}")
            return False
        
        authorized = mt5.login(
            login=int(MT5_LOGIN),
            password=MT5_PASSWORD,
            server=MT5_SERVER
        )
        
        if not authorized:
            print(f"Login failed: {mt5.last_error()}")
            mt5.shutdown()
            return False
        
        print(f"✅ Connected to {MT5_SERVER}")
        return True
    
    def log_trade_to_file(self, trade_data):
        """Log trade to JSON file instead of database"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ticket': trade_data.get('ticket'),
            'type': trade_data.get('type'),
            'symbol': trade_data.get('symbol'),
            'lots': trade_data.get('lots'),
            'entry_price': trade_data.get('entry_price'),
            'sl': trade_data.get('sl'),
            'tp': trade_data.get('tp'),
            'strategy': trade_data.get('strategy'),
            'reason': trade_data.get('reason')
        }
        
        # Save to JSON file
        try:
            with open('trades_log.json', 'a') as f:
                f.write(json.dumps(log_entry) + '\\n')
            print(f"📝 Trade logged to trades_log.json")
        except Exception as e:
            print(f"⚠️ Could not log trade: {e}")
            # Store in memory as fallback
            self.trade_log.append(log_entry)
    
    async def monitor_market(self):
        """Simple market monitoring"""
        print("Starting Simple Forex Monitor...")
        
        while True:
            try:
                # Get price
                tick = mt5.symbol_info_tick(SYMBOL)
                if tick:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"{SYMBOL}: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}, "
                          f"Spread={(tick.ask - tick.bid):.5f}")
                
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print("\\nBot stopped by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(10)
    
    def shutdown(self):
        """Clean shutdown"""
        mt5.shutdown()
        
        # Save any in-memory logs
        if self.trade_log:
            try:
                with open('trades_backup.json', 'w') as f:
                    json.dump(self.trade_log, f, indent=2)
                print("💾 Saved trade log to trades_backup.json")
            except:
                pass
        
        print("Bot shutdown complete")

async def main():
    bot = SimpleForexBot()
    
    if not bot.initialize_mt5():
        return
    
    try:
        await bot.monitor_market()
    finally:
        bot.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
'''
    
    with open('simple_bot.py', 'w') as f:
        f.write(simple_bot)
    
    print("✅ Created simple_bot.py (no database required)")
    print("   Run with: python simple_bot.py")

def main():
    """Main fix function"""
    print("🤖 FOREX BOT DATABASE FIX TOOL")
    print("=" * 60)
    
    # Step 1: Check permissions
    check_permissions()
    
    # Step 2: Fix database
    db_path = fix_database_error()
    
    # Step 3: Create alternative bot
    create_simple_bot_without_database()
    
    print("\n" + "=" * 60)
    print("🎯 QUICK FIXES TO TRY:")
    print("=" * 60)
    print("""
    OPTION 1: Use in-memory database
    ---------------------------------
    In your bot code, replace:
        DB_CONFIG['path'] = 'data/trades.db'
    With:
        DB_CONFIG['path'] = ':memory:'
    
    OPTION 2: Use absolute path
    ---------------------------
    Replace with:
        DB_CONFIG['path'] = 'C:/Users/YOURNAME/Documents/trades.db'
    
    OPTION 3: Disable database
    --------------------------
    Set:
        DB_CONFIG['enabled'] = False
    
    OPTION 4: Use simple bot
    ------------------------
    Run: python simple_bot.py
    """)
    
    print(f"\n✅ Your database should now work at: {db_path}")
    print("   Update your config.py with the path above")

if __name__ == '__main__':
    main()