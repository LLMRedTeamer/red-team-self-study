#!/usr/bin/env python3
"""
XKCD Comic Fetcher
- --latest : fetch the latest comic
- --num N  : fetch a specific comic number N
- (no flag): fetch a random comic between 1 and the latest
Saves the image to out/xkcd_<num>.<ext> and prints title/alt/path.
"""

import argparse
import random
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests


API_LATEST = "https://xkcd.com/info.0.json"
API_NUM = "https://xkcd.com/{num}/info.0.json"


def get_json(url: str, timeout: float) -> dict:
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}", file=sys.stderr)
        sys.exit(2)
    except ValueError:
        print("[!] Response was not valid JSON.", file=sys.stderr)
        sys.exit(3)


def guess_extension(img_url: str, resp: requests.Response | None) -> str:
    # Prefer extension from URL path
    ext = Path(urlparse(img_url).path).suffix
    if ext:
        return ext
    # Fallback: try content-type header
    if resp is not None:
        ctype = resp.headers.get("Content-Type", "")
        if "png" in ctype:
            return ".png"
        if "jpeg" in ctype or "jpg" in ctype:
            return ".jpg"
        if "gif" in ctype:
            return ".gif"
    return ".png"


def download_image(img_url: str, out_path: Path, timeout: float) -> None:
    try:
        with requests.get(img_url, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            ext = guess_extension(img_url, r)
            if out_path.suffix != ext:
                out_path = out_path.with_suffix(ext)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"Saved: {out_path}")
    except requests.exceptions.RequestException as e:
        print(f"[!] Image download failed: {e}", file=sys.stderr)
        sys.exit(4)


def main():
    ap = argparse.ArgumentParser(description="Fetch XKCD comics (latest, specific, or random).")
    ap.add_argument("--latest", action="store_true", help="Fetch latest comic")
    ap.add_argument("--num", type=int, help="Fetch specific comic number")
    ap.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds (default: 10)")
    ap.add_argument("--outdir", type=Path, default=Path("out"), help="Directory to save images (default: out/)")
    args = ap.parse_args()

    timeout = args.timeout

    # Decide which comic to fetch
    if args.latest:
        data = get_json(API_LATEST, timeout)
    elif args.num is not None:
        data = get_json(API_NUM.format(num=args.num), timeout)
    else:
        latest = get_json(API_LATEST, timeout)
        latest_num = int(latest.get("num", 1))
        pick = random.randint(1, latest_num)
        data = get_json(API_NUM.format(num=pick), timeout)

    # Extract fields we care about
    try:
        num = int(data["num"])
        title = str(data["title"])
        alt = str(data.get("alt", ""))
        img_url = str(data["img"])
    except KeyError as e:
        print(f"[!] Missing expected field in JSON: {e}", file=sys.stderr)
        sys.exit(5)

    print(f"[Comic #{num}] {title}")
    if alt:
        print(f"Alt: {alt}")
    print(f"Image URL: {img_url}")

    # Save image
    out_path = args.outdir / f"xkcd_{num}"
    download_image(img_url, out_path, timeout)


if __name__ == "__main__":
    main()
