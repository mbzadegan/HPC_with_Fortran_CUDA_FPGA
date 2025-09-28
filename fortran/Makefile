FC      := gfortran
FFLAGS  := -O3 -march=native -fopenmp -Wall
TARGET  := jacobi_cpu
SRC     := jacobi_cpu.f90

all: $(TARGET)

$(TARGET): $(SRC)
	$(FC) $(FFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)
