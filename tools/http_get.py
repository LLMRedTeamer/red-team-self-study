#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
import requests

def main():
    ap = argparse.ArgumentParser(description="HTTP GET helper using requests.")
    ap.add_argument("url", nargs="?", default="https://api.github.com",
                    help="URL to fetch (default: GitHub API root)")
    ap.add_argument("--timeout", type=float, default=10.0,
                    help="Request timeout in seconds (default: 10s)")
    ap.add_argument("--out", type=Path, default=Path("out/response.json"),
                    help="If JSON, save to this path")
    ap.add_argument("--headers", action="store_true",
                    help="Print response headers")
    args = ap.parse_args()

    try:
        resp = requests.get(args.url, timeout=args.timeout)
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}", file=sys.stderr)
        sys.exit(2)

    # Status line
    print(f"URL: {args.url}")
    print(f"Status: {resp.status_code}")

    # Optional headers print
    if args.headers:
        print("\n[Headers]")
        for k, v in resp.headers.items():
            print(f"{k}: {v}")

    # Try JSON first; if parsing fails, fall back to text preview
    try:
        data = resp.json()
        preview = json.dumps(data, indent=2)[:600]
        print("\n[JSON Preview]")
        print(preview + ("\n..." if len(preview) == 600 else ""))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"\n[Saved] JSON to {args.out}")
    except ValueError:
        # Not JSON
        print("\n[Text Preview]")
        text = resp.text
        print(text[:600] + ("\n..." if len(text) > 600 else ""))

if __name__ == "__main__":
    main()

