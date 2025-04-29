from flask import Flask, request, jsonify, render_template
import logging
import requests
import hmac
import hashlib
from uuid import uuid4

# === CONFIG ===
TRUV_CLIENT_ID = 'bd98d755b5184e9f98f58e69eb337069'
TRUV_CLIENT_SECRET = 'sandbox-fab910d3223f95de93a50ba0b053ad8b6d732810'
TRUV_BASE_URL = 'https://prod.truv.com/v1/'

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class TruvClient:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "X-Access-Client-Id": TRUV_CLIENT_ID,
            "X-Access-Secret": TRUV_CLIENT_SECRET,
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json",
        }

    def _request(self, method, endpoint, **kwargs):
        url = TRUV_BASE_URL + endpoint
        headers = kwargs.pop("headers", {})
        headers.update(self.headers)
        response = self.session.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def create_user(self):
        payload = {
            "external_user_id": f"qs-{uuid4().hex}",
            "first_name": "Matthew",
            "last_name": "Hendricks",
            "email": "matthew@example.com"
        }
        return self._request("post", "users/", json=payload)

    def create_bridge_token(self, user_id, product_type="income"):
        payload = {
            "product_type": product_type,
            "tracking_info": "1338-0111-A"
        }
        return self._request("post", f"users/{user_id}/tokens/", json=payload)

    def exchange_public_token(self, public_token):
        payload = {"public_token": public_token}
        return self._request("post", "link-access-tokens/", json=payload)

    def get_income_report(self, access_token):
        return self._request("get", f"link/reports/income/", headers={"Authorization": f"Bearer {access_token}"})

truv = TruvClient()

# === ROUTES ===

@app.route("/", methods=["GET"])
def index():
    user = truv.create_user()
    user_id = user["id"]
    token_info = truv.create_bridge_token(user_id)
    bridge_token = token_info.get("bridge_token")
    return render_template("index.html", bridge_token=bridge_token)

@app.route("/exchange", methods=["POST"])
def exchange_token():
    public_token = request.json.get("public_token")
    if not public_token:
        return jsonify({"error": "Missing public_token"}), 400

    access_info = truv.exchange_public_token(public_token)
    access_token = access_info.get("access_token")

    if not access_token:
        return jsonify({"error": "Failed to exchange token"}), 400

    income_report = truv.get_income_report(access_token)
    return jsonify({"status": "success", "income_report": income_report})

# === START SERVER ===
if __name__ == "__main__":
    app.run(port=5000, debug=True)
