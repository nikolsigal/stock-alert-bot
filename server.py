import os
import requests
from flask import Flask
from telegram import Bot
from telegram.constants import ParseMode
import asyncio
import threading

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
FINNHUB_API_KEY = os.environ.get('FINNHUB_API_KEY')

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return 'הבוט פועל בהצלחה!'

def get_price_finnhub(symbol):
    try:
        url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}'
        res = requests.get(url)
        data = res.json()
        return data['c'], data['pc']
    except:
        return None, None

def get_analyst_recommendation(symbol):
    try:
        url = f'https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={FINNHUB_API_KEY}'
        res = requests.get(url)
        data = res.json()
        if data:
            latest = data[0]
            if latest['buy'] > latest['sell'] and latest['buy'] > latest['hold']:
                return "המלצת אנליסטים: 🟢 לקנות"
            elif latest['sell'] > latest['buy'] and latest['sell'] > latest['hold']:
                return "המלצת אנליסטים: 🔴 למכור"
            else:
                return "המלצת אנליסטים: 🟡 להחזיק"
        else:
            return "המלצת אנליסטים: ❓ לא זמינה"
    except:
        return "המלצת אנליסטים: ❌ שגיאה"

async def send_update():
    symbols = {
        'KTOS': 'KTOS',
        'STNG': 'STNG',
        'XOP': 'XOP',
        'BNO': 'BNO',
        'Ethereum': 'BINANCE:ETHUSDT'
    }

    message = "📊 *עדכון מחירים + המלצות אנליסטים:*\n"
    for name, symbol in symbols.items():
        price, open_price = get_price_finnhub(symbol)
        if price is not None and open_price is not None:
            if price > open_price * 1.01:
                recommendation = "📈 מגמת עלייה – לקנות"
            elif price < open_price * 0.99:
                recommendation = "📉 ירידה – למכור"
            else:
                recommendation = "⏸ יציב – להמתין"
            analyst = get_analyst_recommendation(symbol)
            message += f"{name}: ${price:.2f} – {recommendation}\n{analyst}\n\n"
        else:
            message += f"{name}: ❌ שגיאה בטעינה\n"

    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)

# פונקציה שמריצה את הבוט בת'רד נפרד
def start_background_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_update())

# נפעיל את הבוט ברקע אחרי שהשרת עלה
threading.Thread(target=start_background_loop).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
