import argparse, csv, time, sys
from pathlib import Path
from tqdm import tqdm
from rich.console import Console
from transformers import pipeline

console = Console()

def load_prompts(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def main():
    ap = argparse.ArgumentParser(description="Run prompts through a small HF model and save outputs to CSV.")
    ap.add_argument("--prompts", type=Path, required=True, help="Path to prompts.txt")
    ap.add_argument("--out", type=Path, default=Path("out/results.csv"), help="CSV output path")
    ap.add_argument("--model", default="distilgpt2", help="HF model name (default: distilgpt2)")
    ap.add_argument("--max-new-tokens", type=int, default=60, help="Max new tokens per generation")
    args = ap.parse_args()

    prompts = load_prompts(args.prompts)
    if not prompts:
        console.print("[red]No prompts found.[/red]")
        sys.exit(1)

    console.print(f"[bold]Loading model:[/bold] {args.model}")
    # Force PyTorch to avoid TF/Keras issues
    gen = pipeline("text-generation", model=args.model, framework="pt", device=-1)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["idx","prompt","output","model","ts"])
        writer.writeheader()

        for i, p in enumerate(tqdm(prompts, desc="Running prompts", unit="prompt")):
            out = gen(p, max_new_tokens=args.max_new_tokens, do_sample=False)[0]["generated_text"]
            writer.writerow({
                "idx": i,
                "prompt": p,
                "output": out,
                "model": args.model,
                "ts": int(time.time())
            })

    console.print(f"[green]Saved results to[/green] {args.out}")

if __name__ == "__main__":
    main()
