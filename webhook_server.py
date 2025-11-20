from flask import Flask, request, jsonify
from alpaca_trade_api.rest import REST, APIError
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("APCA_API_BASE_URL")

# Inicializa Flask
app = Flask(__name__)

# Conecta con Alpaca
api = REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=ALPACA_BASE_URL)

@app.route('/')
def home():
    return jsonify({"status": "running", "message": "Webhook server activo ✅"})


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        print("📩 Señal recibida:", data)

        # Validación básica
        if not data or 'symbol' not in data or 'action' not in data or 'qty' not in data:
            print("❌ Señal incompleta o formato inválido")
            return jsonify({"status": "signal rejected", "error": "invalid format"})

        symbol = data['symbol'].upper()
        action = data['action'].upper()
        qty = float(data['qty'])

        # Acción de compra o venta
        if action == 'BUY':
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            print(f"✅ Orden de COMPRA ejecutada: {symbol} x{qty}")
            return jsonify({"status": "order executed", "side": "buy", "symbol": symbol})

        elif action == 'SELL':
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
            print(f"✅ Orden de VENTA ejecutada: {symbol} x{qty}")
            return jsonify({"status": "order executed", "side": "sell", "symbol": symbol})

        else:
            print("⚠️ Acción no reconocida:", action)
            return jsonify({"status": "signal rejected", "error": "unknown action"})

    except APIError as e:
        print("❌ Error de API:", e)
        return jsonify({"status": "error", "message": str(e)})

    except Exception as e:
        print("❌ Error inesperado:", e)
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    print("🚀 Servidor Webhook iniciado en http://127.0.0.1:5000/webhook")
    app.run(host='0.0.0.0', port=5000)
