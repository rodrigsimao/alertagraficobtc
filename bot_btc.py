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
    btc = yf.download("BTC-USD", start="2025-01-01", end=hoje, interval="1d", auto_adjust=False)

    # Verificar colunas necessárias
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in required_cols:
        if col not in btc.columns:
            print(f"Erro: coluna {col} não encontrada nos dados.")
            return

    # Remover linhas com valores ausentes
    btc = btc.dropna(subset=required_cols)

    # Converter todas as colunas para float, valores inválidos viram NaN
    for col in required_cols:
        btc[col] = pd.to_numeric(btc[col], errors='coerce')

    # Remover novamente linhas que viraram NaN
    btc = btc.dropna(subset=required_cols)

    if btc.empty:
        print("Erro: dados não encontrados após limpeza.")
        return

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

    # Enviar imagem via Telegram
    try:
        bot.send_photo(chat_id=CHAT_ID, photo=open(filename, "rb"), caption="📈 Gráfico diário do BTC")
        print(f"Gráfico enviado: {filename}")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

if __name__ == "__main__":
    enviar_grafico()
