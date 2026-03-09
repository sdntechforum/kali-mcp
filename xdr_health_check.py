import requests
import sys
import json

# Configuration - Replace with your actual Cisco XDR details
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
# Regional URL: visibility.amp.cisco.com (US) or visibility.eu.amp.cisco.com (EU)
BASE_URL = "https://visibility.amp.cisco.com" 

def get_token():
    auth_url = f"{BASE_URL}/iroh/oauth2/token"
    response = requests.post(
        auth_url,
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Auth Failed: {response.status_code} - {response.text}")
        sys.exit(1)

def check_health(token):
    # Testing the 'Enrich' API as a baseline health check
    health_url = f"{BASE_URL}/iroh/iroh-enrich/health"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(health_url, headers=headers)
    return response.json()

if __name__ == "__main__":
    print("[*] Contacting Cisco XDR API...")
    token = get_token()
    status = check_health(token)
    print(f"[+] Connection Successful!")
    print(json.dumps(status, indent=2))
