from flask import Flask, request, jsonify
import alpaca_trade_api as tradeapi
import os
import traceback

app = Flask(__name__)

# Cargar claves
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("APCA_API_BASE_URL")

print("🔑 Claves cargadas correctamente")
print("API KEY:", ALPACA_API_KEY)
print("BASE URL:", ALPACA_BASE_URL)

# Inicializar la API
api = tradeapi.REST(
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
    ALPACA_BASE_URL,
    api_version='v2'
)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("📩 Webhook recibido")

        data = request.get_json()
        print("➡️ JSON recibido:", data)

        if not data:
            print("❌ JSON inválido")
            return jsonify({"error": "invalid json"}), 400

        symbol = data.get("symbol")
        action = data.get("action")
        qty = int(data.get("qty"))

        print(f"📌 Procesando: {action} {qty} {symbol}")

        if action.upper() == "BUY":
            api.submit_order(symbol=symbol, qty=qty, side="buy", type="market", time_in_force="gtc")
            print("🟢 Orden de COMPRA enviada")

        elif action.upper() == "SELL":
            api.submit_order(symbol=symbol, qty=qty, side="sell", type="market", time_in_force="gtc")
            print("🔴 Orden de VENTA enviada")

        else:
            print("❌ Acción inválida:", action)
            return jsonify({"error": "invalid action"}), 400

        return jsonify({"status": "order sent"}), 200

    except Exception as e:
        print("🔥 ERROR EN EL WEBHOOK")
        print(str(e))
        traceback.print_exc()
        return jsonify({"error": "internal server error"}), 500


@app.route("/", methods=["GET"])
def home():
    return "🚀 Webhook Trading Bot ONLINE", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
