# Truv Borrower Loan Prototype

This is a proof-of-concept application demonstrating how a borrower can connect their payroll account via Truv, verify income and employment status, and accept a loan offer with automatically generated payroll deductions.

Built with ❤️

---

##  Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/YOUR-USERNAME/UnambiguousProjectName.git
cd UnambiguousProjectName
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Configuration

Create a file called `config.py` in the project root:

```python
# config.py

TRUV_CLIENT_ID = 'your-truv-client-id'
TRUV_CLIENT_SECRET = 'your-truv-client-secret'
TRUV_BASE_URL = 'https://prod.truv.com/v1/'
SECRET_KEY = 'your-flask-session-secret-key'
```

> **Important:**  
> `config.py` is listed in `.gitignore` and should NOT be pushed to GitHub!

---

## 🏁 How to Run

```bash
python app.py
```

- Open your browser and visit `http://localhost:5000/dashboard`
- Start the borrower flow from there!

---

## 📋 Features

- Secure payroll connection via Truv Bridge
- Automatic pulling of borrower's income and employment information
- Intelligent sanity checks (minimum income & active employment required)
- Pre-qualified loan offer if borrower passes checks
- Borrower selects loan amount and repayment term
- Automatic generation of a simple payroll deduction schedule
- All borrower attempts tracked and viewable in the internal dashboard
- Clean separation of secrets using config files
- Ready for sandbox or production environments

---

## 📂 Project Structure

```
/UnambiguousProjectName/
├── app.py             # Main Flask app
├── config.py          # Config file (not pushed to GitHub)
├── requirements.txt   # Python dependencies
├── .gitignore         # Files and folders Git should ignore
├── README.md          # This file
└── templates/         # Frontend HTML templates
    ├── index.html
    ├── income_report.html
    ├── loan_offer.html
    ├── loan_rejected.html
    ├── loan_accepted.html
    └── dashboard.html
```

---

##  Notes

- This is a prototype for internal demo and proof-of-concept purposes.
- For production, session storage should be moved to a persistent database like Redis.
- Real deduction schedules should align with actual pay dates and employer agreements.
- Further enhancements: borrower document uploads, real payroll switches, webhook listening.
