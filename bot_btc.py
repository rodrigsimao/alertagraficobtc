import os
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import asyncio
from telegram import Bot

# ================= Configurações =================
TOKEN = os.environ.get("TELEGRAM_TOKEN")      # GitHub Secret
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")  # GitHub Secret
# =================================================

async def enviar_telegram(filename):
    bot = Bot(token=TOKEN)
    with open(filename, "rb") as photo:
        await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption="📈 Gráfico diário do BTC")

def preparar_grafico():
    hoje = pd.Timestamp.today().strftime('%Y-%m-%d')
    btc = yf.download("BTC-USD", start="2025-01-01", end=hoje, interval="1d", auto_adjust=False)

    # Debug completo do DataFrame
    print("DEBUG: DataFrame baixado do yfinance:")
    print(btc.head())
    print("DEBUG: Colunas originais:", btc.columns.tolist())

    # Se MultiIndex, simplificar
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = btc.columns.get_level_values(0)
        print("DEBUG: MultiIndex detectado, colunas simplificadas:", btc.columns.tolist())

    # Colunas obrigatórias
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_cols = [col for col in required_cols if col not in btc.columns]
    if missing_cols:
        print(f"ERRO: colunas ausentes: {missing_cols}")
        return None

    # Limpeza e conversão para float
    btc = btc.dropna(subset=required_cols)
    for col in required_cols:
        btc[col] = pd.to_numeric(btc[col], errors='coerce')
    btc = btc.dropna(subset=required_cols)

    if btc.empty:
        print("ERRO: DataFrame vazio após limpeza.")
        return None

    # Nome do arquivo diário
    filename = f"btc_candle_{pd.Timestamp.today().strftime('%Y%m%d')}.png"

    # Gerar gráfico de candles
    mpf.plot(
        btc,
        type='candle',
        style='charles',
        title='Bitcoin BTC-USD Diário',
        ylabel='Preço (USD)',
        volume=True,
        savefig=filename
    )

    return filename

def main():
    arquivo = preparar_grafico()
    if arquivo:
        asyncio.run(enviar_telegram(arquivo))
        print(f"Gráfico enviado: {arquivo}")

if __name__ == "__main__":
    main()
