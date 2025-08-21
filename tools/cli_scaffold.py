# tools/cli_scaffold.py
import argparse, json, sys
from pathlib import Path
import requests
import logging
from logging.handlers import RotatingFileHandler

def verbosity_to_level(v: int) -> int:
    # 0 -> WARNING, 1 -> INFO, 2+ -> DEBUG
    return logging.WARNING if v <= 0 else (logging.INFO if v == 1 else logging.DEBUG)

def get_logger(name: str, verbose: int, logfile: Path = Path("logs/app.log")) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # capture everything; handlers filter
    if logger.handlers:             # don’t double-attach if called again
        return logger

    # console
    ch = logging.StreamHandler()
    ch.setLevel(verbosity_to_level(verbose))
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    # file (rotating)
    logfile.parent.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(logfile, maxBytes=512_000, backupCount=3, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))

    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


def fetch_and_save(url: str, timeout: float, out: Path, verbose: int, logger: logging.Logger | None = None) -> dict:
    """Fetch URL, save JSON or text to `out`. Return summary for tests."""
    if logger is None:
        logger = logging.getLogger(__name__)
    logger.debug(f"fetch_and_save called url={url} timeout={timeout} out={out}")

    try:
        logger.info(f"GET {url}")
        resp = requests.get(url, timeout=timeout)
        logger.info(f"Response {resp.status_code} for {url}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        print(f"[!] Request failed: {e}", file=sys.stderr)  # keep CLI stderr behavior
        raise

    try:
        data = resp.json()   # may raise ValueError
        logger.debug("Parsed JSON response")
    except ValueError:
        data = None
        logger.debug("Non-JSON response; falling back to text")

    out.parent.mkdir(parents=True, exist_ok=True)
    if data is not None:
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        kind = "json"
    else:
        out.write_text(resp.text, encoding="utf-8")
        kind = "text"

    logger.info(f"Saved {kind} -> {out}")
    return {"status": resp.status_code, "kind": kind, "out": str(out)}

def main():
    parser = argparse.ArgumentParser(description="Argument Parser")
    parser.add_argument('--url', default='https://httpbin.org/json', help='URL to pull')
    parser.add_argument('--timeout', type=float, default=10.0, help='Timeout (s)')
    parser.add_argument('--out', type=Path, default=Path("out/httpbin.json"), help='Output file path')
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help="Increase verbosity (stackable -v -vv -vvv)")
    args = parser.parse_args()

    logger = get_logger(__name__, args.verbose)
    logger.debug(f"CLI args: url={args.url} timeout={args.timeout} out={args.out} verbose={args.verbose}")

    try:
        info = fetch_and_save(args.url, args.timeout, args.out, args.verbose, logger=logger)
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

