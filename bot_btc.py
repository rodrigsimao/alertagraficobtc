import os
import yfinance as yf
import pandas as pd
import mplfinance as mpf
from telegram import Bot

# ================= Configurações =================
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Pega do GitHub Secrets
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")  # Pega do GitHub Secrets
# =================================================

bot = Bot(token=TOKEN)

def enviar_grafico():
    hoje = pd.Timestamp.today().strftime('%Y-%m-%d')
    
    # Baixar dados históricos do BTC
    btc = yf.download("BTC-USD", start="2025-01-01", end=hoje, interval="1d")
    
    # Limpar linhas com valores ausentes
    btc = btc.dropna(subset=['Open', 'High', 'Low', 'Close'])
    
    # Garantir que todas as colunas estão como float
    btc[['Open', 'High', 'Low', 'Close', 'Volume']] = btc[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    
    if btc.empty:
        print("Erro: dados não encontrados.")
        return

    # Nome do arquivo com data para evitar sobrescrever
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

    # Enviar imagem via Telegram
    try:
        bot.send_photo(chat_id=CHAT_ID, photo=open(filename, "rb"), caption="📈 Gráfico diário do BTC")
        print(f"Gráfico enviado: {filename}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

if __name__ == "__main__":
    enviar_grafico()
