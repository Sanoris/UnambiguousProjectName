import requests

# Fill these out with your Truv sandbox or production credentials
TRUV_CLIENT_ID = 'bd98d755b5184e9f98f58e69eb337069'
TRUV_CLIENT_SECRET = 'sandbox-fab910d3223f95de93a50ba0b053ad8b6d732810'
TRUV_BASE_URL = 'https://prod.truv.com/v1'

def get_access_token():
    url = f"{TRUV_BASE_URL}/oauth/token"
    payload = {
        "client_id": TRUV_CLIENT_ID,
        "client_secret": TRUV_CLIENT_SECRET
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    token = response.json().get('access_token')
    print(f"Access Token: {token}")
    return token

def initiate_income_verification(access_token, account_number, routing_number):
    url = f"{TRUV_BASE_URL}/income/verifications"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "account_number": account_number,
        "routing_number": routing_number
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    verification_id = response.json().get('id')
    print(f"Verification ID: {verification_id}")
    return verification_id

if __name__ == "__main__":
    # Replace with real account & routing numbers for testing
    account_number = '123456789'
    routing_number = '987654321'

    access_token = get_access_token()
    initiate_income_verification(access_token, account_number, routing_number)
