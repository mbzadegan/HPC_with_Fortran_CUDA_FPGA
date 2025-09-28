#!/usr/bin/env python3
"""
bench.py — run Jacobi binaries and collect CSV results.

This script expects each executable to print ONE CSV line:
backend,precision,N,M,iters,runtime_ms,MLUPS,rel_error

Example run (Fortran CPU):
  ./fortran/jacobi_cpu 1024 1024 500 f64

Usage:
  python3 scripts/bench.py \
      --exe ./fortran/jacobi_cpu \
      --sizes 512 1024 2048 \
      --iters 500 \
      --precisions f64 f32 \
      --repeats 3 \
      --threads 8 \
      --out results/results.csv

Notes:
- The script adds a header if the CSV file does not exist.
- You can pass multiple --exe flags to run several backends in one sweep.
- Set different env vars per-exe with --env 'OMP_NUM_THREADS=8' (can repeat).
"""

import argparse
import csv
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HEADER = ["backend","precision","N","M","iters","runtime_ms","MLUPS","rel_error","exe","timestamp"]

def parse_args():
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--exe", action="append", required=True,
                   help="Path to executable. Repeat to run multiple backends.")
    p.add_argument("--sizes", nargs="+", type=int, default=[512, 1024, 2048],
                   help="Square grid sizes (N=M).")
    p.add_argument("--iters", type=int, default=500, help="Iterations per run.")
    p.add_argument("--precisions", nargs="+", default=["f64","f32"],
                   help="Precisions to test (e.g., f64 f32 f16).")
    p.add_argument("--repeats", type=int, default=1, help="Repeat each configuration.")
    p.add_argument("--threads", type=int, default=None, help="OMP threads (if supported).")
    p.add_argument("--env", action="append", default=[],
                   help="Extra env VAR=VALUE (can repeat).")
    p.add_argument("--out", default="results/results.csv", help="Output CSV file.")
    return p.parse_args()

def ensure_header(out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not out_path.exists() or out_path.stat().st_size == 0:
        with out_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)

def run_once(exe, N, iters, precision, env, threads):
    # We assume N=M (square); adapt if needed.
    cmd = [exe, str(N), str(N), str(iters), precision]
    run_env = os.environ.copy()
    if threads is not None:
        run_env["OMP_NUM_THREADS"] = str(threads)
    # Add extra envs
    for item in env:
        if "=" in item:
            k,v = item.split("=",1)
            run_env[k] = v

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=run_env, check=True, text=True)
    except FileNotFoundError:
        print(f"[ERROR] Executable not found: {exe}", file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed ({exe}): {e.stderr}", file=sys.stderr)
        return None

    # Expect a single CSV line
    line = res.stdout.strip().splitlines()[-1] if res.stdout else ""
    if not line or line.count(",") < 6:
        print(f"[WARN] Output did not look like expected CSV: '{line}'", file=sys.stderr)
        return None

    parts = [s.strip() for s in line.split(",")]
    # Some executables might not include all fields in the exact order;
    # we trust the Fortran program produces: backend,precision,N,M,iters,runtime_ms,MLUPS,rel_error
    if len(parts) < 8:
        print(f"[WARN] CSV had fewer than 8 fields: '{line}'", file=sys.stderr)
        return None

    # Append exe path and timestamp for traceability
    parts = parts[:8] + [exe, datetime.utcnow().isoformat(timespec="seconds")]
    return parts

def main():
    args = parse_args()
    out_path = Path(args.out).resolve()
    ensure_header(out_path)

    rows = []
    for exe in args.exe:
        for N in args.sizes:
            for precision in args.precisions:
                for r in range(args.repeats):
                    print(f"Running: exe={exe} N={N} M={N} iters={args.iters} precision={precision} repeat={r+1}/{args.repeats}")
                    row = run_once(exe, N, args.iters, precision, args.env, args.threads)
                    if row:
                        rows.append(row)

    if rows:
        with out_path.open("a", newline="") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)
        print(f"Wrote {len(rows)} rows to {out_path}")
    else:
        print("No rows written; check errors above.")

if __name__ == "__main__":
    main()
