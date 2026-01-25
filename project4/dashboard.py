from flask import Flask, render_template, jsonify
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import json
from config import *

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('data/trades.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/trades')
def get_trades():
    conn = get_db_connection()
    df = pd.read_sql_query('''
        SELECT * FROM trades 
        ORDER BY timestamp DESC 
        LIMIT 50
    ''', conn)
    conn.close()
    return jsonify(df.to_dict('records'))

@app.route('/api/performance')
def get_performance():
    conn = get_db_connection()
    
    # Calculate metrics
    df = pd.read_sql_query('''
        SELECT * FROM trades 
        WHERE timestamp >= datetime('now', '-30 days')
    ''', conn)
    
    if df.empty:
        return jsonify({})
    
    total_trades = len(df)
    winning_trades = len(df[df['profit'] > 0])
    losing_trades = len(df[df['profit'] < 0])
    total_profit = df['profit'].sum()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Daily performance
    daily_df = pd.read_sql_query('''
        SELECT date(timestamp) as date, 
               SUM(profit) as daily_profit,
               COUNT(*) as trades_count
        FROM trades
        GROUP BY date(timestamp)
        ORDER BY date DESC
        LIMIT 30
    ''', conn)
    
    conn.close()
    
    return jsonify({
        'summary': {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'total_profit': total_profit,
            'win_rate': win_rate
        },
        'daily': daily_df.to_dict('records')
    })

@app.route('/api/market')
def get_market():
    # This would connect to MT5 to get real-time data
    # For now, return sample data
    return jsonify({
        'symbol': SYMBOL,
        'bid': 3800.50,
        'ask': 3801.00,
        'spread': 0.50,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)