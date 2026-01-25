import requests
import logging
from config import TELEGRAM_CONFIG

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot_token = TELEGRAM_CONFIG['bot_token']
        self.chat_id = TELEGRAM_CONFIG['chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_message(self, message: str):
        """Send message to Telegram"""
        if not TELEGRAM_CONFIG['enabled']:
            return
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 200:
                logger.error(f"Telegram send failed: {response.text}")
        except Exception as e:
            logger.error(f"Telegram error: {e}")
    
    def send_trade_alert(self, trade_data: dict):
        """Send formatted trade alert"""
        emoji = "🟢" if trade_data['type'] == 'BUY' else "🔴"
        message = f"""
{emoji} <b>TRADE ALERT</b> {emoji}
        
<b>Action:</b> {trade_data['type']}
<b>Symbol:</b> {trade_data['symbol']}
<b>Price:</b> {trade_data['price']:.5f}
<b>Lots:</b> {trade_data['lots']}
<b>SL:</b> {trade_data['sl']:.5f}
<b>TP:</b> {trade_data['tp']:.5f}
<b>Strategy:</b> {trade_data['strategy']}
        
📊 <b>Account Info</b>
Balance: ${trade_data['balance']:.2f}
Equity: ${trade_data['equity']:.2f}
        """
        self.send_message(message)