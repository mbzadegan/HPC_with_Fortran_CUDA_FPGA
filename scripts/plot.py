#!/usr/bin/env python3
"""
plot.py — generate figures from results/results.csv

Input CSV header (append-only; created by bench.py):
backend,precision,N,M,iters,runtime_ms,MLUPS,rel_error,exe,timestamp

Outputs (saved in results/):
- throughput_vs_size.png      : MLUPS vs size (N), grouped by backend+precision
- error_vs_throughput.png     : rel_error vs MLUPS scatter, grouped by backend+precision
- resources_future.png        : placeholder if you later add FPGA resource CSV

Usage:
  python3 scripts/plot.py --csv results/results.csv --outdir results/

Notes:
- Expects numeric columns for N, MLUPS, rel_error, etc.
- One chart per figure (no subplots), matplotlib only, default styles.
"""
import argparse
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def parse_args():
    ap = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument("--csv", default="results/results.csv", help="Input results CSV.")
    ap.add_argument("--outdir", default="results", help="Output directory for plots.")
    return ap.parse_args()

def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    df = pd.read_csv(path)
    # Basic type enforcement
    for col in ["N","M","iters"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["runtime_ms","MLUPS","rel_error"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def throughput_vs_size(df: pd.DataFrame, outpath: Path):
    # Create a combined label "backend-precision"
    df = df.copy()
    df["label"] = df["backend"].astype(str) + "-" + df["precision"].astype(str)
    labels = sorted(df["label"].unique())

    plt.figure()  # new figure; no subplots
    # For each label, plot mean MLUPS per size
    for lab in labels:
        sub = df[df["label"] == lab].groupby("N", as_index=False)["MLUPS"].mean()
        sub = sub.sort_values("N")
        plt.plot(sub["N"], sub["MLUPS"], marker="o", label=lab)
    plt.xlabel("Grid size N (N=M)")
    plt.ylabel("Throughput (MLUPS)")
    plt.title("Throughput vs Size")
    plt.legend()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()

def error_vs_throughput(df: pd.DataFrame, outpath: Path):
    df = df.copy()
    df["label"] = df["backend"].astype(str) + "-" + df["precision"].astype(str)
    labels = sorted(df["label"].unique())

    plt.figure()  # new figure
    for lab in labels:
        sub = df[df["label"] == lab]
        plt.scatter(sub["MLUPS"], sub["rel_error"], label=lab, alpha=0.8)
    plt.xlabel("Throughput (MLUPS)")
    plt.ylabel("Relative error vs reference")
    plt.title("Error vs Throughput")
    plt.yscale("log")  # log scale often helpful for error
    plt.legend()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()

def main():
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = load_csv(Path(args.csv))
    # Drop rows with NaNs in critical columns
    df = df.dropna(subset=["N","MLUPS","rel_error","backend","precision"])

    throughput_vs_size(df, outdir / "throughput_vs_size.png")
    error_vs_throughput(df, outdir / "error_vs_throughput.png")

    print(f"Wrote plots to {outdir}")

if __name__ == "__main__":
    main()
