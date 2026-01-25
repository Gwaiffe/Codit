import json
import pandas as pd
from datetime import datetime

def analyze_trades():
    try:
        with open('trades_log.json', 'r') as f:
            lines = f.readlines()
        
        trades = [json.loads(line) for line in lines]
        df = pd.DataFrame(trades)
        
        print('=' * 50)
        print('TRADE ANALYSIS REPORT')
        print('=' * 50)
        print(f'Total Trades: {len(df)}')
        print(f'Buy Trades: {len(df[df["type"] == "BUY"])}')
        print(f'Sell Trades: {len(df[df["type"] == "SELL"])}')
        
        if len(df) > 0:
            # Calculate win rate (simplified - you'd need actual P&L)
            print('\nLast 5 Trades:')
            print(df.tail(5).to_string(index=False))
            
            # Save to CSV for Excel analysis
            df.to_csv('trades_analysis.csv', index=False)
            print('\nAnalysis saved to trades_analysis.csv')
    
    except FileNotFoundError:
        print('No trade log found. Run the bot first.')

if __name__ == '__main__':
    analyze_trades()