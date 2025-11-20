# 
# Usage: To re-create this platform project launch xsct with below options.
# xsct C:\DevWorks\UDP\Vitis_tcp\UDP\platform.tcl
# 
# OR launch xsct and run below command.
# source C:\DevWorks\UDP\Vitis_tcp\UDP\platform.tcl
# 
# To create the platform in a different location, modify the -out option of "platform create" command.
# -out option specifies the output directory of the platform project.

platform create -name {UDP}\
-hw {C:\DevWorks\UDP\Vivado\UDP_Vivado\UDP.xsa}\
-out {C:/DevWorks/UDP/Vitis_tcp}

platform write
domain create -name {freertos10_xilinx_ps7_cortexa9_0} -display-name {freertos10_xilinx_ps7_cortexa9_0} -os {freertos10_xilinx} -proc {ps7_cortexa9_0} -runtime {cpp} -arch {32-bit} -support-app {freertos_lwip_echo_server}
platform generate -domains 
platform active {UDP}
domain active {zynq_fsbl}
domain active {freertos10_xilinx_ps7_cortexa9_0}
platform generate -quick
platform generate
