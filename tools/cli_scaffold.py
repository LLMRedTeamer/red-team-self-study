# tools/cli_scaffold.py
import argparse, json, sys
from pathlib import Path
import requests

def fetch_and_save(url: str, timeout: float, out: Path, verbose: int) -> dict:
    """Fetch URL, save JSON or text to `out`. Return summary for tests."""
    try:
        resp = requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as e:
        # print to stderr for CLI users
        print(f"[!] Request failed: {e}", file=sys.stderr)
        # in library mode, bubble up a clear signal
        raise

    data = None
    try:
        data = resp.json()   # may raise ValueError
    except ValueError:
        data = None

    out.parent.mkdir(parents=True, exist_ok=True)
    if data is not None:
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        kind = "json"
    else:
        out.write_text(resp.text, encoding="utf-8")
        kind = "text"

    return {"status": resp.status_code, "kind": kind, "out": str(out)}

def main():
    parser = argparse.ArgumentParser(description="Argument Parser")
    parser.add_argument('--url', default='https://httpbin.org/json', help='URL to pull')
    parser.add_argument('--timeout', type=float, default=10.0, help='Timeout (s)')
    parser.add_argument('--out', type=Path, default=Path("out/httpbin.json"), help='Output file path')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Increase verbosity (stackable -v -vv -vvv)")
    args = parser.parse_args()

    try:
        info = fetch_and_save(args.url, args.timeout, args.out, args.verbose)
    except requests.exceptions.RequestException:
        sys.exit(2)

    if args.verbose >= 1:
        print(f"Status: {info['status']}")
    if args.verbose >= 3:
        # small preview
        txt = Path(info["out"]).read_text(encoding="utf-8")
        print(txt[:600] + ("\n..." if len(txt) > 600 else ""))

if __name__ == "__main__":
    main()

