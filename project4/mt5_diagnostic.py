import MetaTrader5 as mt5
import platform
import os
import sys

print("=" * 60)
print("MT5 DIAGNOSTIC TOOL")
print("=" * 60)

# Check Python and OS info
print(f"Python Version: {platform.python_version()}")
print(f"Operating System: {platform.system()} {platform.release()}")
print(f"Architecture: {platform.architecture()[0]}")

# Check MT5 installation
print("\n🔍 Checking MT5 Installation...")
mt5_paths = [
    "C:/Program Files/MetaTrader 5/terminal64.exe",
    "C:/Program Files (x86)/MetaTrader 5/terminal64.exe",
    "C:/Program Files/MetaTrader 5/terminal.exe",
    "C:/Program Files (x86)/MetaTrader 5/terminal.exe",
    os.path.expanduser("~/AppData/Local/Programs/MetaTrader 5/terminal64.exe"),
    os.path.expanduser("~/AppData/Local/Programs/MetaTrader 5/terminal.exe"),
]

mt5_installed = False
for path in mt5_paths:
    if os.path.exists(path):
        print(f"✓ MT5 Found: {path}")
        mt5_installed = True
        break

if not mt5_installed:
    print("✗ MT5 not found in standard locations")

# Check MetaTrader5 package
print(f"\n🔍 MetaTrader5 Package: {mt5.__version__ if hasattr(mt5, '__version__') else 'N/A'}")

# Try to initialize
print("\n🔍 Attempting MT5 Initialization...")
try:
    # Try without parameters first
    print("Trying initialize() without parameters...")
    if mt5.initialize():
        print("✓ MT5 initialized successfully")
        
        # Try to login with demo
        print("\n🔍 Testing Demo Login...")
        
        # EXNESS DEMO SERVERS (Try these):
        demo_servers = [
            'Exness-Demo',  # Standard demo
            'Exness-Demo2',  # Alternative
            'Exness-Demo3',  # Another alternative
            'Exness-MT5Trial7',  # Trial server
            'Exness-MT5Trial',  # Another trial
            'ExnessReal',  # Sometimes demo works on real server
        ]
        
        for server in demo_servers:
            print(f"\nTrying server: {server}")
            try:
                # Common demo credentials (Exness defaults)
                login = 123456  # Replace with YOUR demo account number
                password = "your_demo_password"  # Replace with YOUR password
                server = server
                
                authorized = mt5.login(login=login, password=password, server=server)
                if authorized:
                    print(f"✓ Login successful to {server}")
                    account_info = mt5.account_info()
                    print(f"  Account: {account_info.login}")
                    print(f"  Balance: ${account_info.balance:.2f}")
                    print(f"  Server: {account_info.server}")
                    break
                else:
                    print(f"✗ Login failed: {mt5.last_error()}")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        mt5.shutdown()
    else:
        error_code = mt5.last_error()
        print(f"✗ MT5 initialization failed")
        print(f"  Error Code: {error_code}")
        print(f"  Error Message: {self.get_error_description(error_code)}")
        
except Exception as e:
    print(f"✗ Exception during initialization: {e}")

# Check if MT5 is running
print("\n🔍 Checking if MT5 is running...")
import psutil

mt5_running = False
for proc in psutil.process_iter(['name']):
    try:
        if 'terminal' in proc.info['name'].lower() or 'metatrader' in proc.info['name'].lower():
            print(f"✓ MT5 is running (PID: {proc.pid})")
            mt5_running = True
            break
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

if not mt5_running:
    print("✗ MT5 is not running")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

def get_error_description(error_code):
    """Get human-readable error description"""
    error_descriptions = {
        1: "TRADE_RETCODE_REQUOTE - Requote",
        2: "TRADE_RETCODE_REJECT - Request rejected",
        3: "TRADE_RETCODE_CANCEL - Request canceled by trader",
        4: "TRADE_RETCODE_PLACED - Order placed",
        5: "TRADE_RETCODE_DONE - Request completed",
        6: "TRADE_RETCODE_DONE_PARTIAL - Request partially completed",
        7: "TRADE_RETCODE_ERROR - Request processing error",
        8: "TRADE_RETCODE_TIMEOUT - Request timeout",
        9: "TRADE_RETCODE_INVALID - Invalid request",
        10: "TRADE_RETCODE_INVALID_VOLUME - Invalid volume",
        11: "TRADE_RETCODE_INVALID_PRICE - Invalid price",
        12: "TRADE_RETCODE_INVALID_STOPS - Invalid stops",
        13: "TRADE_RETCODE_TRADE_DISABLED - Trade disabled",
        14: "TRADE_RETCODE_MARKET_CLOSED - Market closed",
        15: "TRADE_RETCODE_NO_MONEY - Not enough money",
        16: "TRADE_RETCODE_PRICE_CHANGED - Price changed",
        17: "TRADE_RETCODE_PRICE_OFF - No quotes",
        18: "TRADE_RETCODE_INVALID_EXPIRATION - Invalid expiration",
        19: "TRADE_RETCODE_ORDER_CHANGED - Order changed",
        20: "TRADE_RETCODE_TOO_MANY_REQUESTS - Too many requests",
        21: "TRADE_RETCODE_NO_CHANGES - No changes",
        22: "TRADE_RETCODE_SERVER_DISABLES_AT - Autotrading disabled",
        23: "TRADE_RETCODE_CLIENT_DISABLES_AT - Autotrading disabled by client",
        24: "TRADE_RETCODE_LOCKED - Request locked",
        25: "TRADE_RETCODE_FROZEN - Order or position frozen",
        26: "TRADE_RETCODE_INVALID_FILL - Invalid fill",
        27: "TRADE_RETCODE_CONNECTION - No connection",
        28: "TRADE_RETCODE_ONLY_REAL - Only real allowed",
        29: "TRADE_RETCODE_LIMIT_ORDERS - Limit orders allowed",
        30: "TRADE_RETCODE_LIMIT_VOLUME - Limit volume exceeded",
        10004: "Invalid login credentials",
        10006: "Invalid account number",
        10013: "Invalid parameters",
        10014: "Trade session is busy",
        10015: "Old version of the client terminal",
        10016: "No connection with trade server",
        10017: "Not enough rights",
        10018: "Too frequent requests",
        10019: "Malfunctional trade operation",
        10020: "Account disabled",
        10021: "Invalid account",
        10022: "Trade timeout",
        10023: "Invalid price",
        10024: "Invalid stops",
        10025: "Invalid trade volume",
        10026: "Market closed",
        10027: "Trade disabled",
        10028: "Not enough money",
        10029: "Price changed",
        10030: "Off quotes",
        10031: "Invalid expiration",
        10032: "Order changed",
    }
    return error_descriptions.get(error_code, f"Unknown error: {error_code}")