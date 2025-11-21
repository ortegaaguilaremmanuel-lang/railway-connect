from flask import Flask, request, jsonify
import alpaca_trade_api as tradeapi
import os
import traceback

app = Flask(__name__)

# Cargar claves desde variables de entorno de Render
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("APCA_API_BASE_URL")

print("🔑 Claves cargadas correctamente")
print("API KEY:", ALPACA_API_KEY)
print("BASE URL:", ALPACA_BASE_URL)

# Inicializar API de Alpaca
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
            print("❌ JSON inválido recibido")
            return jsonify({"error": "invalid json"}), 400

        symbol = data.get("symbol")
        action = data.get("action").upper()
        qty = int(data.get("qty"))

        print(f"📌 Procesando operación: {action} {qty} {symbol}")

        # Obtener precio actual del activo
        last_quote = api.get_latest_quote(symbol)
        market_price = last_quote.ask_price
        print(f"💲 Precio de mercado actual para {symbol}: {market_price}")

        # Ejecutar operación
        if action == "BUY":
            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side="buy",
                type="market",
                time_in_force="gtc"
            )
            print(f"🟢 ORDEN DE COMPRA enviada: {order.id}")

        elif action == "SELL":
            # revisar posición actual
            try:
                position = api.get_position(symbol)
                current_qty = int(position.qty)
                print(f"📊 Cantidad actual en cartera: {current_qty}")

                if qty > current_qty:
                    print("❌ ERROR: No tienes suficientes acciones para vender")
                    return jsonify({"error": "not enough shares"}), 400

            except Exception:
                print("❌ ERROR: No se encontró posición para vender")
                return jsonify({"error": "no position"}), 400

            order = api.submit_order(
                symbol=symbol,
                qty=qty,
                side="sell",
                type="market",
                time_in_force="gtc"
            )
            print(f"🔴 ORDEN DE VENTA enviada: {order.id}")

        else:
            print("❌ Acción inválida:", action)
            return jsonify({"error": "invalid action"}), 400

        # Calcular ganancia/pérdida después de la operación
        try:
            position = api.get_position(symbol)
            avg_entry = float(position.avg_entry_price)
            current_price = float(position.current_price)
            unrealized_pl = float(position.unrealized_pl)

            print(f"📈 Precio promedio entrada: {avg_entry}")
            print(f"📉 Precio actual: {current_price}")
            print(f"💰 Ganancia/Pérdida: {unrealized_pl}")

        except Exception:
            print("⚠️ No es posible calcular P/L ahora (probable venta total).")

        return jsonify({"status": "order sent"}), 200

    except Exception as e:
        print("🔥 ERROR EN EL SERVIDOR:")
        print(str(e))
        traceback.print_exc()
        return jsonify({"error": "internal server error"}), 500


@app.route("/", methods=["GET"])
def home():
    return "🚀 Webhook Trading Bot ONLINE", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
