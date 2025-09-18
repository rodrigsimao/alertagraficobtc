import os
import yfinance as yf
import pandas as pd
import mplfinance as mpf
from telegram import Bot

# ================= Configurações =================
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # GitHub Secret
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")  # GitHub Secret
# =================================================

def enviar_grafico():
    hoje = pd.Timestamp.today().strftime('%Y-%m-%d')
    
    # Baixar dados históricos do BTC
    btc = yf.download("BTC-USD", start="2025-01-01", end=hoje, interval="1d", auto_adjust=False)

    print("DEBUG: DataFrame baixado do yfinance:")
    print(btc.head())
    print("DEBUG: Colunas originais:", btc.columns.tolist())

    # Se MultiIndex, simplificar
    if isinstance(btc.columns, pd.MultiIndex):
        btc.columns = btc.columns.get_level_values(0)
        print("DEBUG: MultiIndex detectado, colunas simplificadas:", btc.columns.tolist())

    # Colunas obrigatórias
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    # Verificar se todas as colunas existem
    missing_cols = [col for col in required_cols if col not in btc.columns]
    if missing_cols:
        print(f"ERRO: colunas ausentes: {missing_cols}")
        print("DEBUG: colunas disponíveis:", btc.columns.tolist())
        return

    # Limpar dados inválidos
    btc = btc.dropna(subset=required_cols)
    for col in required_cols:
        btc[col] = pd.to_numeric(btc[col], errors='coerce')
    btc = btc.dropna(subset=required_cols)

    if btc.empty:
        print("ERRO: DataFrame vazio após limpeza.")
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

    # Enviar imagem via Telegram usando API síncrona
    try:
        bot = Bot(token=TOKEN)
        with open(filename, "rb") as photo:
            bot.send_photo(chat_id=CHAT_ID, photo=photo, caption="📈 Gráfico diário do BTC")
        print(f"Gráfico enviado: {filename}")
    except Exception as e:
        print(f"ERRO ao enviar mensagem: {e}")

if __name__ == "__main__":
    enviar_grafico()
