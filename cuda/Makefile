CUDA_HOME ?= /usr/local/cuda
NVCC := $(CUDA_HOME)/bin/nvcc
NVFLAGS := -O3 -arch=sm_60

TARGET := jacobi_cuda
SRC := jacobi_cuda.cu

all: $(TARGET)

$(TARGET): $(SRC)
	$(NVCC) $(NVFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)
