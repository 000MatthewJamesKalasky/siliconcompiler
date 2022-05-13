# Default constraints file that sets up clocks based on definitions in schema.

source sc_manifest.tcl

set sc_design [dict get $sc_cfg design]

foreach pin [dict keys [dict get $sc_cfg datasheet $sc_design pin]] {
    if {[dict get $sc_cfg datasheet $sc_design pin $pin type global] == "clk"} {
        # If clock...

        set period_str [dict get $sc_cfg datasheet $sc_design pin $pin tperiod global]
        set periodtuple [regsub -all {[\,\)\(]} $period_str " "]
        set period [lindex $periodtuple 1]
        set period_ns [expr $period * pow(10, 9)]

        create_clock [get_ports $pin] -name $pin  -period $period_ns
    }
}
