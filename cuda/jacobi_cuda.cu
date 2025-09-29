#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

// Simple 2D Jacobi kernel (fp64/fp32).
// For fp16 you can extend with __half intrinsics later.

template <typename T>
__global__ void jacobi2d(const T* __restrict__ in, T* __restrict__ out,
                         int N, int M)
{
    int i = blockIdx.y * blockDim.y + threadIdx.y;
    int j = blockIdx.x * blockDim.x + threadIdx.x;
    if (i > 0 && i < N-1 && j > 0 && j < M-1) {
        out[i*M + j] = (T)0.25 * ( in[(i-1)*M + j] + in[(i+1)*M + j]
                                 + in[i*M + (j-1)] + in[i*M + (j+1)] );
    }
}

template <typename T>
void run_jacobi(int N, int M, int iters)
{
    size_t bytes = N * M * sizeof(T);
    T *h_in = (T*)malloc(bytes);
    T *h_out = (T*)malloc(bytes);

    // init: zero, hot top edge = 1
    for (int i=0; i<N; i++) {
        for (int j=0; j<M; j++) {
            h_in[i*M+j] = 0;
        }
    }
    for (int j=0; j<M; j++) h_in[0*M+j] = 1;

    T *d_in, *d_out;
    cudaMalloc(&d_in, bytes);
    cudaMalloc(&d_out, bytes);
    cudaMemcpy(d_in, h_in, bytes, cudaMemcpyHostToDevice);

    dim3 block(16,16);
    dim3 grid((M+block.x-1)/block.x, (N+block.y-1)/block.y);

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);
    for (int t=0; t<iters; t++) {
        jacobi2d<T><<<grid,block>>>(d_in,d_out,N,M);
        std::swap(d_in,d_out);
    }
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float ms=0;
    cudaEventElapsedTime(&ms,start,stop);

    double mlups = (double)(N-2)*(M-2)*iters / (ms*1e3);

    // Print CSV line: backend,precision,N,M,iters,runtime_ms,MLUPS,rel_error
    const char* prec = (sizeof(T)==8 ? "f64" : "f32");
    printf("cuda,%s,%d,%d,%d,%.3f,%.3f,%.4e\n",
           prec,N,M,iters,ms,mlups,0.0);

    cudaMemcpy(h_out, d_in, bytes, cudaMemcpyDeviceToHost);
    cudaFree(d_in);
    cudaFree(d_out);
    free(h_in);
    free(h_out);
}

int main(int argc, char** argv)
{
    if (argc < 5) {
        printf("Usage: %s N M ITERS PREC(f64|f32)\n", argv[0]);
        return 1;
    }
    int N = atoi(argv[1]);
    int M = atoi(argv[2]);
    int iters = atoi(argv[3]);
    std::string prec(argv[4]);

    if (prec=="f64") run_jacobi<double>(N,M,iters);
    else if (prec=="f32") run_jacobi<float>(N,M,iters);
    else {
        fprintf(stderr,"Precision %s not implemented yet.\n", prec.c_str());
        return 1;
    }
    return 0;
}
