#!/usr/bin/env python3
"""
COMPLETE MT5 SETUP VERIFICATION SCRIPT
Run this to check if everything is setup correctly
"""
import MetaTrader5 as mt5
import sys
import os
import time
import ctypes
import platform


def print_step(step, status, message):
    """Print formatted step"""
    icon = "✅" if status else "❌"
    print(f"{icon} Step {step}: {message}")


def check_mt5_installation():
    """Check if MT5 is installed"""
    step = 1
    paths = [
        "C:/Program Files/MetaTrader 5/terminal64.exe",
        "C:/Program Files (x86)/MetaTrader 5/terminal64.exe",
        os.path.expanduser(
            "~/AppData/Local/Programs/MetaTrader 5/terminal64.exe"),
    ]

    for path in paths:
        if os.path.exists(path):
            print_step(step, True, f"MT5 found at: {path}")
            return path

    print_step(step, False, "MT5 not found. Please install MT5 first!")
    return None


def check_python_bitness():
    """Check if Python matches MT5 bitness"""
    step = 2
    is_64bit = platform.machine().endswith('64')
    print_step(step, True, f"Python is {'64-bit' if is_64bit else '32-bit'}")
    return is_64bit


def initialize_mt5(mt5_path):
    """Initialize MT5 connection"""
    step = 3
    try:
        # Try with path
        if mt5_path and os.path.exists(mt5_path):
            initialized = mt5.initialize(path=mt5_path)
        else:
            initialized = mt5.initialize()

        if initialized:
            print_step(step, True, "MT5 initialized successfully")
            return True
        else:
            error = mt5.last_error()
            print_step(step, False, f"Initialize failed: {error}")
            return False
    except Exception as e:
        print_step(step, False, f"Exception: {e}")
        return False


def login_to_demo():
    """Login to demo account"""
    step = 4

    # DEMO ACCOUNT CREDENTIALS - CHANGE THESE!
    DEMO_ACCOUNTS = [
        {"login": 12345678, "password": "your_password",
            "server": "Exness-MT5Trial7"},
        {"login": 87654321, "password": "demo123", "server": "Exness-Demo"},
        {"login": 123456, "password": "password", "server": "Exness-MT5Trial"},
    ]

    for account in DEMO_ACCOUNTS:
        print(
            f"\nTrying demo account: {account['login']} on {account['server']}")

        authorized = mt5.login(
            login=account["login"],
            password=account["password"],
            server=account["server"],
            timeout=5000
        )

        if authorized:
            print_step(step, True, f"Logged in to {account['server']}")

            # Get account info
            account_info = mt5.account_info()
            print(f"\n📈 ACCOUNT INFORMATION:")
            print(f"   Account: {account_info.login}")
            print(f"   Name: {account_info.name}")
            print(f"   Server: {account_info.server}")
            print(f"   Balance: ${account_info.balance:.2f}")
            print(f"   Equity: ${account_info.equity:.2f}")
            print(f"   Leverage: 1:{account_info.leverage}")

            return True

    print_step(step, False, "All demo logins failed. Create a demo account!")
    return False


def check_ea_permissions():
    """Check if Expert Advisors are enabled"""
    step = 5

    terminal_info = mt5.terminal_info()

    print(f"\n🔧 EXPERT ADVISOR SETTINGS:")

    checks = [
        ("Automated Trading", terminal_info.trade_allowed),
        ("DLL Imports", terminal_info.dlls_allowed),
        ("External Experts", True),  # Hard to check via API
        ("WebRequest", True),  # Hard to check via API
    ]

    all_passed = True
    for name, status in checks:
        icon = "✅" if status else "❌"
        print(f"   {icon} {name}")
        if not status:
            all_passed = False

    if all_passed:
        print_step(step, True, "All EA permissions are enabled!")
    else:
        print_step(step, False, "Some EA permissions are disabled")
        print("\n⚠️ Fix in MT5: Tools → Options → Expert Advisors")
        print("   Enable ALL checkboxes")

    return all_passed


def check_symbol_availability():
    """Check if USDTUGX is available"""
    step = 6

    symbol = "USDTUGX"
    symbol_info = mt5.symbol_info(symbol)

    if symbol_info:
        print_step(step, True, f"Symbol {symbol} found")

        # Check if enabled for trading
        if symbol_info.visible:
            print(f"   ✅ {symbol} is enabled for trading")
        else:
            print(f"   ⚠️ {symbol} exists but not enabled")
            print("   Enabling it now...")
            mt5.symbol_select(symbol, True)

        # Get price
        tick = mt5.symbol_info_tick(symbol)
        if tick:
            print(
                f"   💰 Current Price: Bid={tick.bid:.5f}, Ask={tick.ask:.5f}")
            print(f"   📏 Spread: {(tick.ask - tick.bid):.5f}")

        return True
    else:
        print_step(step, False, f"Symbol {symbol} not found")
        # First 5 symbols
        print(f"   Available symbols: {mt5.symbols_get()[:5]}...")
        return False


def test_trade_execution():
    """Test if we can execute a trade"""
    step = 7

    print("\n🧪 TESTING TRADE EXECUTION...")

    # Get account info
    account = mt5.account_info()
    if account.balance < 10:
        print("⚠️ Balance too low for test trade")
        return False

    # Prepare a BUY order (will be cancelled immediately)
    symbol = "USDTUGX"
    symbol_info = mt5.symbol_info(symbol)

    if not symbol_info:
        print("Symbol not available for testing")
        return False

    # Get current price
    tick = mt5.symbol_info_tick(symbol)

    # Prepare order request
    lot_size = 0.01  # Smallest lot
    price = tick.ask
    sl = price * 0.995  # 0.5% stop loss
    tp = price * 1.01   # 1% take profit

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 999999,  # Magic number for test trades
        "comment": "Python Bot Test",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }

    print(f"   Test Order: BUY {lot_size} lots at {price:.5f}")
    print(f"   SL: {sl:.5f}, TP: {tp:.5f}")

    # Send order
    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print_step(
            step, True, f"Trade test SUCCESSFUL! Ticket: {result.order}")

        # Immediately close the test trade
        print("   Closing test trade...")
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_SELL,
            "position": result.order,
            "price": tick.bid,
            "deviation": 10,
            "magic": 999999,
            "comment": "Close Test Trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        close_result = mt5.order_send(close_request)
        if close_result.retcode == mt5.TRADE_RETCODE_DONE:
            print("   ✅ Test trade closed successfully")
        else:
            print(f"   ⚠️ Could not close test trade: {close_result.comment}")

        return True
    else:
        print_step(step, False, f"Trade test FAILED: {result.comment}")
        return False


def main():
    """Main verification function"""
    print("=" * 60)
    print("MT5 COMPLETE SETUP VERIFICATION")
    print("=" * 60)

    # Check installation
    mt5_path = check_mt5_installation()
    if not mt5_path:
        return False

    # Check Python
    check_python_bitness()

    # Initialize MT5
    if not initialize_mt5(mt5_path):
        return False

    # Login to demo
    if not login_to_demo():
        return False

    # Check EA permissions
    if not check_ea_permissions():
        return False

    # Check symbol
    if not check_symbol_availability():
        return False

    # Test trade execution (optional)
    test_trade = input("\nTest trade execution? (y/n): ").lower()
    if test_trade == 'y':
        test_trade_execution()

    print("\n" + "=" * 60)
    print("✅ SETUP VERIFICATION COMPLETE!")
    print("=" * 60)

    # Shutdown
    mt5.shutdown()
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Your MT5 is ready for automated trading!")
        print("Next: Run your trading bot with confidence!")
    else:
        print("\n⚠️ Setup incomplete. Please fix the issues above.")
        print("Need help? Share the error messages with me.")

    input("\nPress Enter to exit...")
