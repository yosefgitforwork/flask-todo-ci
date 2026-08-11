"""Tiny integration smoke test, run inside the compose network by CI.

Hits the JSON API the way a real client would and checks the 201 create
contract. Uses only the standard library so the test image needs no pip install.
"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE_URL = "http://backend:5000"  # the compose service name


def try_create():
    payload = json.dumps({"title": "Buy groceries"}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/api/todos",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        body = json.loads(resp.read())
        return resp.status, body


def main():
    # The backend may still be booting; retry for a while before giving up.
    for attempt in range(1, 31):
        try:
            status, body = try_create()
            if status == 201 and body.get("title") == "Buy groceries":
                print("TEST PASSED:", body)
                return 0
            print("TEST FAILED: unexpected response", status, body)
            return 1
        except urllib.error.URLError as exc:
            print(f"attempt {attempt}: backend not ready ({exc}); retrying...")
            time.sleep(2)

    print("TEST FAILED: backend never became reachable")
    return 1


if __name__ == "__main__":
    sys.exit(main())
