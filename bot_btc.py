import os
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import asyncio
from telegram import Bot

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def enviar_telegram(filename, legenda):
    bot = Bot(token=TOKEN)
    with open(filename, "rb") as photo:
        await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=legenda)

def baixar_btc_usd():
    hoje = pd.Timestamp.today().strftime('%Y-%m-%d')
    btc_usd = yf.download("BTC-USD", start="2025-01-01", end=hoje, interval="1d", auto_adjust=False)
    print("DEBUG: BTC-USD baixado")
    print(btc_usd.head())
    
    if isinstance(btc_usd.columns, pd.MultiIndex):
        btc_usd.columns = btc_usd.columns.get_level_values(0)

    required_cols = ['Open','High','Low','Close','Volume']
    btc_usd = btc_usd.dropna(subset=required_cols)
    for col in required_cols:
        btc_usd[col] = pd.to_numeric(btc_usd[col], errors='coerce')
    btc_usd = btc_usd.dropna(subset=required_cols)
    return btc_usd

def calcular_btc_brl(btc_usd):
    usd_brl = yf.download("BRL=X", start="2025-01-01", end=pd.Timestamp.today().strftime('%Y-%m-%d'), interval="1d", auto_adjust=False)
    print("DEBUG: USD-BRL baixado")
    print(usd_brl.head())
    
    if isinstance(usd_brl.columns, pd.MultiIndex):
        usd_brl.columns = usd_brl.columns.get_level_values(0)
    
    usd_brl = usd_brl[['Close']].rename(columns={'Close':'USD-BRL'})
    usd_brl['USD-BRL'] = pd.to_numeric(usd_brl['USD-BRL'], errors='coerce')
    usd_brl = usd_brl.dropna()

    # Mesclar datas e calcular BTC-BRL
    btc_brl = btc_usd.copy()
    btc_brl = btc_brl.join(usd_brl, how='inner')
    btc_brl['Open'] = btc_brl['Open'] * btc_brl['USD-BRL']
    btc_brl['High'] = btc_brl['High'] * btc_brl['USD-BRL']
    btc_brl['Low'] = btc_brl['Low'] * btc_brl['USD-BRL']
    btc_brl['Close'] = btc_brl['Close'] * btc_brl['USD-BRL']
    # Volume em USD → podemos manter igual ou converter para BRL
    return btc_brl[['Open','High','Low','Close','Volume']]

def gerar_grafico(btc, moeda_label):
    filename = f"{moeda_label}_candle_{pd.Timestamp.today().strftime('%Y%m%d')}.png"
    mpf.plot(
        btc,
        type='candle',
        style='charles',
        title=f'Bitcoin Diário ({moeda_label})',
        ylabel=f'Preço ({moeda_label})',
        volume=True,
        savefig=filename
    )
    return filename

def main():
    btc_usd = baixar_btc_usd()
    btc_brl = calcular_btc_brl(btc_usd)

    # Gerar gráficos
    arquivo_usd = gerar_grafico(btc_usd, "USD")
    arquivo_brl = gerar_grafico(btc_brl, "BRL")

    # Enviar via Telegram
    asyncio.run(enviar_telegram(arquivo_usd, "📈 Gráfico diário BTC/USD"))
    asyncio.run(enviar_telegram(arquivo_brl, "📈 Gráfico diário BTC/BRL"))

    print(f"Gráficos enviados: {arquivo_usd} e {arquivo_brl}")

if __name__ == "__main__":
    main()
