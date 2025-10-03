# Design Document: Mixed-Precision 2D Jacobi on CPU, GPU, and FPGA

## 1. Problem Statement

The **2D Jacobi method** is an iterative solver widely used in scientific computing to approximate solutions of partial differential equations (e.g., Laplace’s equation, heat diffusion).  
Each grid point is updated to the average of its four neighbors:

\[
u^{(t+1)}_{i,j} = \frac{1}{4}\left(u^{(t)}_{i-1,j} + u^{(t)}_{i+1,j} + u^{(t)}_{i,j-1} + u^{(t)}_{i,j+1}\right)
\]

- Boundary conditions remain fixed.
- Iterations continue until convergence or a fixed number of steps.

This stencil is **memory-bound**, making it a canonical benchmark for heterogeneous computing (CPU, GPU, FPGA).

---

## 2. Project Goals

- Implement the Jacobi 2D stencil on **three backends**:
  - **CPU (Fortran + OpenMP)** — baseline and reference
  - **GPU (CUDA)** — exploit fine-grained parallelism
  - **FPGA (HLS)** — explore streaming, pipelined design

- Evaluate across **precisions**:
  - **fp64** (double)
  - **fp32** (single)
  - **fp16 / fixed16** (half precision)

- Metrics:
  - **Throughput (MLUPS)** — million lattice updates per second
  - **Runtime (ms)**
  - **Relative error** against fp64 reference
  - **Resource usage (FPGA):** LUTs, BRAM, DSPs, Fmax (from synthesis reports)

---

## 3. Experiment Plan

### Parameters
- Grid sizes: `512 × 512`, `1024 × 1024`, `2048 × 2048`
- Iterations: `500`
- Boundary condition: **top edge = 1.0, others = 0.0**

### Backends
1. **CPU (Fortran + OpenMP)**
   - Parallelize outer loop with OpenMP
   - Use as reference (fp64 run = ground truth)
2. **GPU (CUDA)**
   - Grid-stride loops, 2D thread blocks
   - Variants: fp64, fp32, fp16 (`__half` or tensor cores)
3. **FPGA (HLS)**
   - C/C++ kernel in Vitis/Intel HLS
   - Line buffer + sliding window
   - Pragmas: `PIPELINE II=1`, `ARRAY_PARTITION`, `DATAFLOW`
   - Collect csynth reports for throughput/resource estimates

---

## 4. Methodology

- **Automation:**  
  `scripts/bench.py` — runs all executables and appends results to `results/results.csv`.

- **Visualization:**  
  `scripts/plot.py` — generates:
  - Throughput vs grid size (per backend/precision)
  - Relative error vs throughput

- **Analysis:**  
  Compare performance trade-offs across backends and precisions.  
  FPGA estimates are included alongside measured CPU/GPU results.

---

## 5. Expected Outcomes

- **CPU (fp64):** Baseline, correct but slower.
- **GPU (fp16/fp32):** Large speedups with acceptable error.
- **FPGA (HLS):** Pipeline design achieves II=1; competitive throughput estimates; lower energy (future hardware runs).

---

## 6. Future Extensions

- Real FPGA hardware evaluation (board or AWS F1).
- DragonFlyBSD vs Linux system study (CPU portability)
- Mixed-precision auto-tuning (adaptive precision selection)
- Multi-GPU scaling or MPI + CUDA + FPGA hybrid orchestration
