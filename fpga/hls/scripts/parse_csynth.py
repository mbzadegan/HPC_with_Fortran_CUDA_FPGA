#!/usr/bin/env python3
"""
parse_csynth.py — extract key metrics from Vitis HLS csynth report and compute throughput estimates.

Usage:
  python3 fpga/hls/scripts/parse_csynth.py \
      --report fpga/hls/jacobi_hls/solution1/syn/report/jacobi2d_hls_csynth.rpt \
      --N 1024 --M 1024 --iters 500 \
      --out results/fpga_estimates.csv

Output CSV columns:
backend,precision,N,M,iters,clock_ns,Fmax_MHz,Latency_min,Latency_max,II,MLUPS_est,BRAM18K,DSP,FF,LUT
"""
import re, argparse, csv, os
from pathlib import Path
from datetime import datetime

HEADER = ["backend","precision","N","M","iters","clock_ns","Fmax_MHz",
          "Latency_min","Latency_max","II","MLUPS_est","BRAM18K","DSP","FF","LUT","report","timestamp"]

def parse_report(text: str):
    # Clock period
    clock_ns = None
    m = re.search(r"Estimated\s+Clock\s+Period\s*:\s*([\d\.]+)\s*ns", text, re.I)
    if m: clock_ns = float(m.group(1))

    # Latency section
    lat_min = lat_max = II = None
    m = re.search(r"Latency.*?min\s*=\s*(\d+).*\n.*?max\s*=\s*(\d+).*?\n.*?II\s*=\s*(\d+)", text, re.S|re.I)
    if m:
        lat_min = int(m.group(1)); lat_max = int(m.group(2)); II = int(m.group(3))
    else:
        # Alternate format lines
        m2 = re.search(r"Latency\s*\(cycles\)\s*min\s*=\s*(\d+)\s*max\s*=\s*(\d+)\s*average\s*=\s*\d+", text, re.I)
        if m2:
            lat_min = int(m2.group(1)); lat_max = int(m2.group(2))
        m3 = re.search(r"Interval\s*\(II\)\s*=\s*(\d+)", text, re.I)
        if m3: II = int(m3.group(1))

    # Resources
    bram = dsp = ff = lut = None
    m = re.search(r"BRAM_18K\s*\|\s*(\d+)", text);  bram = int(m.group(1)) if m else None
    m = re.search(r"DSP48E.*?\|\s*(\d+)", text);    dsp  = int(m.group(1)) if m else None
    m = re.search(r"FF\s*\|\s*(\d+)", text);        ff   = int(m.group(1)) if m else None
    m = re.search(r"LUT\s*\|\s*(\d+)", text);       lut  = int(m.group(1)) if m else None

    return clock_ns, lat_min, lat_max, II, bram, dsp, ff, lut

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    ap.add_argument("--N", type=int, required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--iters", type=int, required=True)
    ap.add_argument("--precision", default="fixed16")  # label only
    ap.add_argument("--out", default="results/fpga_estimates.csv")
    args = ap.parse_args()

    rpt_path = Path(args.report)
    text = rpt_path.read_text(encoding="utf-8", errors="ignore")

    clock_ns, lat_min, lat_max, II, bram, dsp, ff, lut = parse_report(text)
    if clock_ns is None or II is None:
        raise SystemExit("Could not parse clock period or II from report.")

    fmax_mhz = 1000.0/clock_ns
    # Throughput estimate (cells/sec) for one iteration at II cycles/cell:
    # cells_per_sec = fmax / II
    # For T iterations in testbench calling kernel T times, MLUPS approximates similarly per call.
    mlups_est = (fmax_mhz * 1e6 / II) / 1e6  # = fmax(Hz)/II scaled to mega-updates/s
    # Multiply by (N-2)*(M-2) / cycles? Here we report core rate (per-cell) as MLUPS;
    # Users can scale by active cells if desired. Keep it simple & comparable across sizes.

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = (not out_path.exists()) or (out_path.stat().st_size == 0)
    with out_path.open("a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(HEADER)
        w.writerow([
            "fpga_est", args.precision, args.N, args.M, args.iters,
            f"{clock_ns:.3f}", f"{fmax_mhz:.2f}",
            lat_min if lat_min is not None else "",
            lat_max if lat_max is not None else "",
            II if II is not None else "",
            f"{mlups_est:.3f}",
            bram if bram is not None else "",
            dsp if dsp is not None else "",
            ff if ff is not None else "",
            lut if lut is not None else "",
            str(rpt_path), 
            datetime.utcnow().isoformat(timespec="seconds")
        ])
    print(f"Wrote estimate to {out_path}")

if __name__ == "__main__":
    main()
