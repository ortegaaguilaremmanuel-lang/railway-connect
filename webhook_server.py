from flask import Flask, request, jsonify
import alpaca_trade_api as tradeapi
import os
import traceback

app = Flask(__name__)

# ============================
#  CARGAR VARIABLES DE ENTORNO
# ============================
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("APCA_API_BASE_URL")

print("🔑 Claves cargadas correctamente")
print("API KEY:", ALPACA_API_KEY)
print("BASE URL:", ALPACA_BASE_URL)

# ============================
#  INICIALIZAR API ALPACA
# ============================
try:
    api = tradeapi.REST(
        ALPACA_API_KEY,
        ALPACA_SECRET_KEY,
        ALPACA_BASE_URL,
        api_version='v2'
    )
    print("🚀 API conectada con éxito")
except Exception as e:
    print("❌ ERROR al conectar Alpaca:")
    print(str(e))
    traceback.print_exc()


# ============================
#       ENDPOINT WEBHOOK
# ============================
@app.route("/webhook", methods=["POST"])
def webhook():
    print("📩 Webhook recibido")

    try:
        data = request.get_json()
        print("➡️ JSON recibido:", data)

        if not data:
            print("❌ JSON inválido")
            return jsonify({"error": "invalid json"}), 400

        symbol = data.get("symbol")
        action = data.get("action")
        qty = data.get("qty")

        if not symbol or not action or not qty:
            print("❌ Faltan datos")
            return jsonify({"error": "missing fields"}), 400

        qty = int(qty)
        action = action.upper()

        print(f"📌 Procesando {action} {qty} {symbol}")

        # =====================
        #   COMPRA
        # =====================
        if action == "BUY":
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side="buy",
                type="market",
                time_in_force="gtc"
            )
            print("🟢 ORDEN DE COMPRA ENVIADA:", order.id)
            return jsonify({"status": "BUY sent", "order_id": order.id})

        # =====================
        #   VENTA
        # =====================
        elif action == "SELL":
            # Validar si tienes posiciones
            try:
                position = api.get_position(symbol)
                available_qty = int(position.qty)
                print(f"📊 Tienes {available_qty} acciones en posición")

                if available_qty < qty:
                    print("❌ No tienes suficientes acciones")
                    return jsonify({"error": "not enough position"}), 400

            except Exception:
                print("❌ No tienes posiciones abiertas")
                return jsonify({"error": "no open position"}), 400

            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side="sell",
                type="market",
                time_in_force="gtc"
            )
            print("🔴 ORDEN DE VENTA ENVIADA:", order.id)
            return jsonify({"status": "SELL sent", "order_id": order.id})

        else:
            print("❌ Acción inválida:", action)
            return jsonify({"error": "invalid action"}), 400

    except Exception as e:
        print("🔥 ERROR EN EL WEBHOOK")
        print(str(e))
        traceback.print_exc()
        return jsonify({"error": "internal server error"}), 500


# ============================
#       HOME PAGE
# ============================
@app.route("/", methods=["GET"])
def home():
    return "🚀 Webhook Trading Bot ONLINE", 200


# ============================
#   INICIAR SERVIDOR
# ============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
