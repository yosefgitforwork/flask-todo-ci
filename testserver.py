import requests
import time
import sys

BASE_URL = "http://web:5000"  # שם ה-service בדוקר
URL = f"{BASE_URL}/add"

data = {
    "title": "Buy groceries"
}


if __name__ == "__main__":
    try:
        response = requests.post(URL, json=data)

        if response.status_code == 200:
            print("TEST PASSED:", response.json())
            sys.exit(0)
        else:
            print("TEST FAILED: bad status code", response.status_code)
            sys.exit(1)

    except Exception as e:
        print("TEST FAILED:", str(e))
        sys.exit(1)