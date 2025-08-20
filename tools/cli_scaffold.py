import argparse
import requests
import json
import sys
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument Parser")
    parser.add_argument('--url', default='https://httpbin.org/json', help='URL to pull')
    parser.add_argument('--timeout', type=float, default=10.0, help='Timeout duration (seconds)')
    parser.add_argument('--out', type=Path, default=Path("out/httpbin.json"), help='Output file path')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Increase verbosity (stackable: -v, -vv, -vvv)")
    args = parser.parse_args()

    # Network call with error handling
    try:
        response = requests.get(args.url, timeout=args.timeout)
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}", file=sys.stderr)
        sys.exit(2)

    # Verbosity
    if args.verbose >= 1:
        print(f"Status: {response.status_code}")
    if args.verbose >= 2:
        for k, v in response.headers.items():
            print(f"{k}: {v}")

    # Decide JSON vs text
    data = None
    try:
        data = response.json()   # raises ValueError if not JSON
    except ValueError:
        data = None

    # Ensure out dir & save
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if data is not None:
        args.out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        args.out.write_text(response.text, encoding="utf-8")

    # Optional preview
    if args.verbose >= 3:
        preview = json.dumps(data, indent=2) if data is not None else response.text
        print(preview[:600] + ("\n..." if len(preview) > 600 else ""))

