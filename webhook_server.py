from flask import Flask, request, jsonify
import alpaca_trade_api as tradeapi
import os

app = Flask(__name__)

# 🔐 Variables de entorno para Render
ALPACA_API_KEY = os.getenv("APCA_API_KEY_ID")
ALPACA_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("APCA_API_BASE_URL")

# 🔗 Cliente Alpaca
api = tradeapi.REST(
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
    ALPACA_BASE_URL,
    api_version='v2'
)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON received"}), 400

    symbol = data.get("symbol")
    action = data.get("action")
    qty = int(data.get("qty", 1))

    if not symbol or not action:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        if action.upper() == "BUY":
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
        elif action.upper() == "SELL":
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side='sell',
                type='market',
                time_in_force='gtc'
            )
        else:
            return jsonify({"error": "Invalid action"}), 400

        return jsonify({"status": "success", "action": action, "symbol": symbol})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "Trading Bot Running OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
