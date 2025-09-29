// tb_jacobi_hls.cpp — C testbench for Vitis HLS
#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <vector>
#include <algorithm>

extern "C" void jacobi2d_hls(const float *in, float *out, int N, int M);

// Initialize grid with top edge = 1.0, others = 0.0
static void init_grid(std::vector<float>& a, int N, int M) {
    std::fill(a.begin(), a.end(), 0.0f);
    for (int j=0; j<M; ++j) a[j] = 1.0f; // row 0
}

int main(int argc, char** argv) {
    int N = 1024, M = 1024, iters = 10;
    if (argc >= 3) { N = std::atoi(argv[1]); M = std::atoi(argv[2]); }
    if (argc >= 4) { iters = std::atoi(argv[3]); }

    std::vector<float> a(N*M), b(N*M);
    init_grid(a, N, M);
    b = a;

    // Perform 'iters' iterations by alternating input/output buffers.
    for (int t=0; t<iters; ++t) {
        jacobi2d_hls(a.data(), b.data(), N, M);
        std::swap(a, b);
    }

    // Simple checksum to aid regression
    double sum = 0.0;
    for (int i=0; i<N*M; ++i) sum += a[i];
    printf("HLS csim done: N=%d M=%d iters=%d checksum=%.6f\n", N, M, iters, sum);
    return 0;
}
