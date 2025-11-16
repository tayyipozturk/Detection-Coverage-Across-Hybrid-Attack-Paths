import os
import json
import requests

MITRE_URL = (
    "https://raw.githubusercontent.com/mitre/cti/master/"
    "enterprise-attack/enterprise-attack.json"
)
OUT = os.path.join("data", "enterprise-attack.json")


def download_mitre():
    os.makedirs("data", exist_ok=True)
    print(f"[+] Downloading MITRE ATT&CK Enterprise JSON from {MITRE_URL}")
    resp = requests.get(MITRE_URL)
    resp.raise_for_status()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(resp.json(), f, indent=2)
    print(f"[+] Saved MITRE data to {OUT}")


if __name__ == "__main__":
    download_mitre()
