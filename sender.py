import csv
import requests
from constants import SEND_TO_SERVER, SERVER_URL, OUTPUT_FILE


def send_event(event: dict):
    if SEND_TO_SERVER:
        try:
            response = requests.post(SERVER_URL, json=event, timeout=10.0)

            if response.status_code >= 400:
                print(f"Error sending event: {response.status_code} {response.text}")

        except Exception as e:
            print("POST error:", e)

    else:
        with open(OUTPUT_FILE, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=event.keys())

            if f.tell() == 0:
                writer.writeheader()

            writer.writerow(event)