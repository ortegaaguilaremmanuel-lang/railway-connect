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

# Inicializar API
api = tradeapi.REST(
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
    ALPACA_BASE_URL,
    api_version='v2'
)

print("🚀 API conectada con éxito")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        print("\n📩 Webhook recibido")

        data = request.get_json()
        print("➡️ JSON recibido:", data)

        if not data:
            return jsonify({"error": "invalid json"}), 400

        symbol = data.get("symbol")
        action = data.get("action")
        qty = int(data.get("qty"))

        print(f"📌 Acción: {action}  | Cantidad: {qty} | Símbolo: {symbol}")

        # Obtener precio de mercado
        last_price = api.get_latest_trade(symbol).price
        print(f"💲 Precio actual de {symbol}: {last_price}")

        # Comprar
        if action.upper() == "BUY":
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side="buy",
                type="market",
                time_in_force="gtc"
            )
            print("🟢 ORDEN DE COMPRA enviada:", order.id)
            return jsonify({"order_id": order.id, "status": "BUY sent"}), 200

        # Vender
        elif action.upper() == "SELL":
            # Obtener posición
            try:
                position = api.get_position(symbol)
                avg_price = float(position.avg_entry_price)
                print(f"📘 Precio promedio de entrada: {avg_price}")
            except:
                print("⚠️ No tienes posición abierta en", symbol)
                return jsonify({"error": "no position"}), 400

            # Enviar venta
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side="sell",
                type="market",
                time_in_force="gtc"
            )
            print("🔴 ORDEN DE VENTA enviada:", order.id)

            # Calcular P/L
            profit = round((last_price - avg_price) * qty, 2)
            print(f"📈 Ganancia/Pérdida: {profit}")

            return jsonify({
                "order_id": order.id,
                "status": "SELL sent",
                "profit": profit
            }), 200

        else:
            return jsonify({"error": "invalid action"}), 400

    except Exception as e:
        print("🔥 ERROR:", e)
        traceback.print_exc()
        return jsonify({"error": "internal server error"}), 500


@app.route("/", methods=["GET"])
def home():
    return "🚀 Webhook Trading Bot ONLINE", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
