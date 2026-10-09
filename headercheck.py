import requests
import sys

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
]


def check_headers(url):
    response = requests.get(url, timeout=10)
    results = {}
    for header in SECURITY_HEADERS:
        results[header] = header in response.headers
    return results

def main():
    if len(sys.argv) != 2:
        print("Usage: python headercheck.py <url>")
        sys.exit(2)

    url = sys.argv[1]
    try:
        results = check_headers(url)
    except requests.exceptions.RequestException as error:
        print(f"Error: could not reach {url} ({error})")
        sys.exit(3)

    missing = 0
    for header, present in results.items():
        status = "OK     " if present else "MISSING"
        print(f"[{status}] {header}")
        if not present:
            missing += 1

    print(f"\n{missing} of {len(results)} security headers missing.")
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()