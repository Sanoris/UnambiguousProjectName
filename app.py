from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from config import TRUV_CLIENT_ID, TRUV_CLIENT_SECRET, TRUV_BASE_URL, SECRET_KEY
import logging
import requests
import uuid
import json

app = Flask(__name__)
app.secret_key = SECRET_KEY
logging.basicConfig(level=logging.INFO)

# Temporary memory store
income_reports = {}
borrower_records = []  # Track borrowers

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
            "external_user_id": f"qs-{uuid.uuid4().hex}",
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
        payload = {"access_token": access_token}
        return self._request("post", "link/reports/income/", json=payload)

truv = TruvClient()

def extract_income_and_status(income_report):
    try:
        employments = income_report.get('employments', [])
        if not employments:
            return 0, "UNKNOWN"

        first_employment = employments[0]

        income_annual = float(first_employment.get('income', 0))
        income_unit = first_employment.get('income_unit', 'YEARLY')

        if income_unit == "YEARLY":
            monthly_income = income_annual / 12
        elif income_unit == "MONTHLY":
            monthly_income = income_annual
        else:
            monthly_income = income_annual  # fallback

        is_active = first_employment.get('is_active', False)
        employment_status = "ACTIVE" if is_active else "INACTIVE"

        return monthly_income, employment_status
    except Exception as e:
        logging.error(f"Income/status parse error: {e}")
        return 0, "UNKNOWN"

def passes_sanity_check(gross_income, employment_status):
    return gross_income > 2000 and employment_status == "ACTIVE"

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

    # Store the income report
    report_id = str(uuid.uuid4())
    income_reports[report_id] = income_report
    session['report_id'] = report_id

    # Extract borrower info
    external_user_id = access_info.get('external_user_id', 'unknown')
    gross_income, employment_status = extract_income_and_status(income_report)
    passed = passes_sanity_check(gross_income, employment_status)

    borrower_records.append({
        "external_user_id": external_user_id,
        "gross_income": gross_income,
        "employment_status": employment_status,
        "sanity_passed": passed,
        "loan_status": "Pending"
    })

    # Redirect based on sanity check
    if passed:
        return jsonify({"status": "success", "income_report_url": "/loan_offer"})
    else:
        return jsonify({"status": "fail", "income_report_url": "/loan_rejected"})

@app.route("/loan_offer", methods=["GET"])
def loan_offer():
    report_id = session.get('report_id')
    if not report_id or report_id not in income_reports:
        return "No income report found.", 404

    income_data = income_reports[report_id]
    gross_income, _ = extract_income_and_status(income_data)

    return render_template("loan_offer.html", gross_income=gross_income)

@app.route("/loan_rejected", methods=["GET"])
def loan_rejected():
    if borrower_records:
        borrower_records[-1]["loan_status"] = "Rejected"
    return render_template("loan_rejected.html")

@app.route("/accept_loan", methods=["POST"])
def accept_loan():
    loan_amount = float(request.form.get('loan_amount'))
    repayment_months = int(request.form.get('repayment_months'))

    if borrower_records:
        borrower_records[-1]["loan_status"] = "Accepted"

    deduction_per_month = round(loan_amount / repayment_months, 2)

    return render_template("loan_accepted.html",
                           loan_amount=loan_amount,
                           repayment_months=repayment_months,
                           deduction_per_month=deduction_per_month)

@app.route("/income_report", methods=["GET"])
def view_income_report():
    report_id = session.get('report_id')
    if not report_id or report_id not in income_reports:
        return "No income report found.", 404

    report_data = income_reports[report_id]
    return render_template("income_report.html", report=json.dumps(report_data, indent=4))

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html", borrower_records=borrower_records)

if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)
