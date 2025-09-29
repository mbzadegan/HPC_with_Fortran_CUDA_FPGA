# run_hls.tcl — Vitis HLS non-project flow
# Usage:
#   vitis_hls -f run_hls.tcl

open_project -reset jacobi_hls
set_top jacobi2d_hls
add_files jacobi_hls.cpp
add_files -tb tb_jacobi_hls.cpp

open_solution -reset "solution1"
# Set a generic Zynq ultrascale+ part; change as needed
set_part {xczu7ev-ffvc1156-2-e}
create_clock -period 5 -name default

# C simulation (args: N M iters)
csim_design -argv {1024 1024 10}

# C synthesis
csynth_design

# Optional: Cosimulation (can be time-consuming)
# cosim_design -rtl verilog -argv {1024 1024 10}

export_design -format ip_catalog
exit
