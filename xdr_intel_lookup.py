import requests
import sys
import json

# --- Configuration ---
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
BASE_URL = "https://visibility.amp.cisco.com" # Change to .eu for Europe

def get_token():
    auth_url = f"{BASE_URL}/iroh/oauth2/token"
    res = requests.post(auth_url, auth=(CLIENT_ID, CLIENT_SECRET),
                        data={"grant_type": "client_credentials"})
    return res.json().get("access_token")

def lookup_ip(token, ip_address):
    # The 'observe' endpoint queries all modules (Talos, AMP, etc.) for info on an IP
    url = f"{BASE_URL}/iroh/iroh-enrich/observe/observables"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Cisco XDR uses 'Observables' (type 1 = IP, type 2 = Domain, etc.)
    payload = [{"type": "ip", "value": ip_address}]
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 xdr_intel_lookup.py <IP_ADDRESS>")
        sys.exit(1)

    target_ip = sys.argv[1]
    token = get_token()
    intel_data = lookup_ip(token, target_ip)

    # Simplified output for the AI to read easily
    print(f"--- Threat Intel for {target_ip} ---")
    data = intel_data.get('data', [])
    for entry in data:
        module = entry.get('module', 'Unknown Module')
        verdicts = entry.get('data', {}).get('verdicts', {}).get('docs', [])
        for v in verdicts:
            disposition = v.get('disposition_name', 'Unknown')
            print(f"[{module}] Disposition: {disposition}")
