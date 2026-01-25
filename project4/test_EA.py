# test_ea_permissions.py
import MetaTrader5 as mt5
import os

def test_ea_permissions():
    print("Testing MT5 EA Permissions...")
    
    # Start MT5
    mt5_path = "C:/Program Files/MetaTrader 5/terminal64.exe"
    if not os.path.exists(mt5_path):
        mt5_path = None
    
    if not mt5.initialize(path=mt5_path):
        print(f"❌ MT5 Initialize Failed: {mt5.last_error()}")
        return False
    
    # Check terminal info
    terminal_info = mt5.terminal_info()
    
    print("\n📊 TERMINAL INFORMATION:")
    print(f"  Name: {terminal_info.name}")
    print(f"  Version: {terminal_info.version}")
    print(f"  Build: {terminal_info.build}")
    print(f"  Trade Allowed: {'✅' if terminal_info.trade_allowed else '❌'}")
    print(f"  Trade Mode: {terminal_info.trade_mode}")
    print(f"  DLLs Allowed: {'✅' if terminal_info.dlls_allowed else '❌'}")
    
    # Check if EA trading is enabled
    if not terminal_info.trade_allowed:
        print("\n⚠️ WARNING: Automated trading is NOT enabled!")
        print("Go to: Tools → Options → Expert Advisors")
        print("Check 'Allow automated trading'")
        return False
    
    print("\n✅ EA Permissions are CORRECTLY configured!")
    return True

if __name__ == "__main__":
    test_ea_permissions()