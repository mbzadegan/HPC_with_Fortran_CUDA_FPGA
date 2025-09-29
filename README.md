# Mixed-Precision 2D Jacobi on CPU, GPU, and FPGA (HLS)

This project implements the **2D Jacobi iterative solver** — a classic stencil kernel used in scientific computing — across three backends:

- **Fortran + OpenMP (CPU baseline)**
- **CUDA (GPU, fp64 / fp32 / fp16)**
- **FPGA (High-Level Synthesis, estimated throughput)**

The goal is to study **mixed precision trade-offs** in performance and accuracy across heterogeneous architectures, reflecting modern HPC research challenges.

---

## 🔬 Background

The **2D Jacobi method** solves discretized PDEs (like Laplace’s equation) by repeatedly updating each grid point with the average of its four neighbors.  
It is memory-bandwidth intensive, making it a common **HPC benchmark** for CPUs, GPUs, and FPGAs.

Update rule for iteration `t+1`:

\[
u^{(t+1)}_{i,j} = \tfrac{1}{4} \left(u^{(t)}_{i-1,j} + u^{(t)}_{i+1,j} + u^{(t)}_{i,j-1} + u^{(t)}_{i,j+1}\right)
\]

---

## 📂 Repository Layout

```
fortran/             # Fortran OpenMP Jacobi
  ├─ jacobi_cpu.f90
  └─ Makefile

cuda/                # CUDA GPU version (to be added)
  ├─ jacobi_cuda.cu
  └─ Makefile

fpga/hls/            # FPGA HLS version (to be added)
  ├─ jacobi_hls.cpp
  ├─ tb_jacobi_hls.cpp
  └─ scripts/

scripts/             # Automation tools
  ├─ bench.py        # Run benchmarks, collect results.csv
  └─ plot.py         # Generate throughput/error plots


docs/                # Project documentation
  ├─ design.md
  └─ report.md (convertible to PDF)

(Under Working) results/             # Collected data + figures
  ├─ results.csv
  ├─ throughput_vs_size.png
  └─ error_vs_throughput.png
```

---

## ⚙️ Building

### Fortran CPU version
```bash
cd fortran
make
```
Produces `jacobi_cpu`.

Run example:
```bash
./jacobi_cpu 1024 1024 500 f64
```

This prints a CSV line:
```
cpu,f64,1024,1024,500,1234.567,0.848,0.0000E+00
```

---

## 🏃 Benchmarking

Use the Python benchmarking script to run sweeps and collect results:

```bash
python3 scripts/bench.py   --exe ./fortran/jacobi_cpu   --sizes 512 1024 2048   --iters 500   --precisions f64 f32   --repeats 3   --threads 8   --out results/results.csv
```

You can add multiple executables:
```bash
--exe ./fortran/jacobi_cpu --exe ./cuda/jacobi_cuda
```

---

## 📊 Plotting Results

After benchmarking:
```bash
python3 scripts/plot.py --csv results/results.csv --outdir results/
```

Generates:
- `results/throughput_vs_size.png`
- `results/error_vs_throughput.png`

---

## 📖 Documentation

- `docs/design.md` — design notes and implementation details  
- `docs/report.md` — short paper-style report (convert to PDF for submission)  

---

## 🔮 Future Work

- Add CUDA fp16 kernels (with tensor cores where available)  
- Add FPGA HLS synthesis + cosim results  
- Compare portability across Linux vs DragonflyBSD (CPU baseline)  
- Extend to multi-GPU and hybrid CPU–GPU–FPGA workflows  

---

## License

MIT License.
