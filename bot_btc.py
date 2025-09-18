import os
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import asyncio
from telegram import Bot

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def enviar_telegram(filename, legenda):
    bot = Bot(token=TOKEN)
    with open(filename, "rb") as photo:
        await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=legenda)

def baixar_dados(ticker):
    hoje = pd.Timestamp.today().strftime('%Y-%m-%d')
    btc = yf.download(ticker, start="2025-01-01", end=hoje, interval="1d", auto_adjust=False)
    
    print(f"DEBUG: DataFrame {ticker} baixado")
    print(btc.head())
    
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = btc.columns.get_level_values(0)

    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_cols = [col for col in required_cols if col not in btc.columns]
    if missing_cols:
        print(f"ERRO: colunas ausentes em {ticker}: {missing_cols}")
        return None

    btc = btc.dropna(subset=required_cols)
    for col in required_cols:
        btc[col] = pd.to_numeric(btc[col], errors='coerce')
    btc = btc.dropna(subset=required_cols)

    if btc.empty:
        print(f"ERRO: DataFrame vazio para {ticker}")
        return None

    return btc

def gerar_grafico_combinado(btc_usd, btc_brl):
    filename = f"BTC_USD_BRL_{pd.Timestamp.today().strftime('%Y%m%d')}.png"
    
    # Criar figura com 2 eixos lado a lado
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(12, 10), sharex=True)
    
    # Gráfico BTC/USD
    mpf.plot(
        btc_usd,
        type='candle',
        style='charles',
        ax=axes[0],
        volume=axes[0].twinx(),
        title='Bitcoin BTC/USD Diário',
        ylabel='USD'
    )
    
    # Gráfico BTC/BRL
    mpf.plot(
        btc_brl,
        type='candle',
        style='charles',
        ax=axes[1],
        volume=axes[1].twinx(),
        title='Bitcoin BTC/BRL Diário',
        ylabel='BRL'
    )
    
    plt.tight_layout()
    plt.savefig(filename)
    plt.close(fig)
    
    return filename

def main():
    btc_usd = baixar_dados("BTC-USD")
    btc_brl = baixar_dados("BTC-BRL")

    if btc_usd is None or btc_brl is None:
        print("Erro ao baixar dados. Abortando.")
        return

    arquivo = gerar_grafico_combinado(btc_usd, btc_brl)

    asyncio.run(enviar_telegram(arquivo, "📈 Gráfico diário BTC/USD e BTC/BRL combinados"))
    print(f"Gráfico enviado: {arquivo}")

if __name__ == "__main__":
    main()
