// jacobi_hls.cpp — Vitis HLS top-level for 2D Jacobi (one iteration)
// Notes:
// - Designed for csim/csynth demonstration. Performs ONE Jacobi iteration.
// - Testbench calls this function repeatedly to perform multiple iterations.
// - Interfaces: AXI4 master for in/out, AXI4-Lite control for args.
// - Inner loop is pipelined with II=1.
// - Boundary cells are copied through unchanged (Dirichlet).

#include <ap_int.h>
#include <hls_stream.h>
#include <stdint.h>

extern "C" {
void jacobi2d_hls(const float *in, float *out, int N, int M) {
#pragma HLS INTERFACE m_axi     port=in  offset=slave bundle=gmem depth=1024
#pragma HLS INTERFACE m_axi     port=out offset=slave bundle=gmem depth=1024
#pragma HLS INTERFACE s_axilite port=in   bundle=control
#pragma HLS INTERFACE s_axilite port=out  bundle=control
#pragma HLS INTERFACE s_axilite port=N    bundle=control
#pragma HLS INTERFACE s_axilite port=M    bundle=control
#pragma HLS INTERFACE s_axilite port=return bundle=control

    // Process row by row; pipeline the inner j loop.
Row_Loop:
    for (int i = 0; i < N; i++) {
    Col_Loop:
        for (int j = 0; j < M; j++) {
#pragma HLS PIPELINE II=1
            int idx = i*M + j;
            // Boundaries: copy-through
            if (i == 0 || j == 0 || i == N-1 || j == M-1) {
                out[idx] = in[idx];
            } else {
                float up    = in[(i-1)*M + j];
                float down  = in[(i+1)*M + j];
                float left  = in[i*M + (j-1)];
                float right = in[i*M + (j+1)];
                out[idx] = 0.25f * (up + down + left + right);
            }
        }
    }
}
} // extern "C"
