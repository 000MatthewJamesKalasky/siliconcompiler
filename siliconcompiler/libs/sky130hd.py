import os
import siliconcompiler

def make_docs():
    '''
    Skywater130 standard cell library.
    '''
    chip = siliconcompiler.Chip('<design>')
    setup(chip)
    return chip

def setup(chip):
    foundry = 'skywater'
    process = 'skywater130'
    stackup = '5M1LI'
    version = 'v0_0_2'
    libname = 'sky130hd' # not sure if this should be something else
    libtype = 'unithd' # TODO: update this
    corner = 'typical'

    libdir = os.path.join('..', 'third_party', 'pdks', foundry, process, 'libs', libname, version)

    lib = siliconcompiler.Chip(libname)

    # version
    lib.set('package', 'version', version)

    # footprint/type/sites
    lib.set('asic', 'libarch', libtype)
    lib.set('asic', 'footprint', 'unithd', 'symmetry', 'Y')
    lib.set('asic', 'footprint', 'unithd', 'size', (0.46,2.72))

    lib.set('asic', 'footprint', 'unithddbl', 'symmetry', 'Y')
    lib.set('asic', 'footprint', 'unithddbl', 'size', (0.46,5.44))

    # model files
    lib.add('output', corner, 'nldm', libdir+'/lib/sky130_fd_sc_hd__tt_025C_1v80.lib')
    lib.add('output', stackup, 'lef', libdir+'/lef/sky130_fd_sc_hd_merged.lef')
    lib.add('output', stackup, 'gds', libdir+'/gds/sky130_fd_sc_hd.gds')

    # Power grid specifier
    lib.set('asic', 'pgmetal', 'm1')

    # clock buffers
    lib.add('asic', 'cells', 'clkbuf', 'sky130_fd_sc_hd__clkbuf_1')

    # hold cells
    lib.add('asic', 'cells', 'hold', 'sky130_fd_sc_hd__buf_1')

    # filler
    lib.add('asic', 'cells', 'filler', ['sky130_fd_sc_hd__fill_1',
                                         'sky130_fd_sc_hd__fill_2',
                                         'sky130_fd_sc_hd__fill_4',
                                         'sky130_fd_sc_hd__fill_8'])

    # Tapcell
    lib.add('asic', 'cells','tap', 'sky130_fd_sc_hd__tapvpwrvgnd_1')

    # Endcap
    lib.add('asic', 'cells', 'endcap', 'sky130_fd_sc_hd__decap_4')

    lib.add('asic', 'cells', 'dontuse', [
        'sky130_fd_sc_hd__probe_p_8',
        'sky130_fd_sc_hd__probec_p_8',
        'sky130_fd_sc_hd__lpflow_bleeder_1',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_1',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_16',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_2',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_4',
        'sky130_fd_sc_hd__lpflow_clkbufkapwr_8',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_1',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_16',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_2',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_4',
        'sky130_fd_sc_hd__lpflow_clkinvkapwr_8',
        'sky130_fd_sc_hd__lpflow_decapkapwr_12',
        'sky130_fd_sc_hd__lpflow_decapkapwr_3',
        'sky130_fd_sc_hd__lpflow_decapkapwr_4',
        'sky130_fd_sc_hd__lpflow_decapkapwr_6',
        'sky130_fd_sc_hd__lpflow_decapkapwr_8',
        'sky130_fd_sc_hd__lpflow_inputiso0n_1',
        'sky130_fd_sc_hd__lpflow_inputiso0p_1',
        'sky130_fd_sc_hd__lpflow_inputiso1n_1',
        'sky130_fd_sc_hd__lpflow_inputiso1p_1',
        'sky130_fd_sc_hd__lpflow_inputisolatch_1',
        'sky130_fd_sc_hd__lpflow_isobufsrc_1',
        'sky130_fd_sc_hd__lpflow_isobufsrc_16',
        'sky130_fd_sc_hd__lpflow_isobufsrc_2',
        'sky130_fd_sc_hd__lpflow_isobufsrc_4',
        'sky130_fd_sc_hd__lpflow_isobufsrc_8',
        'sky130_fd_sc_hd__lpflow_isobufsrckapwr_16',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_1',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_2',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_4',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_4',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_1',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_2',
        'sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_4',
        'sky130_fd_sc_hd__buf_16'
    ])

    # driver cell (why empty?)
    lib.add('asic', 'cells', 'driver', '')

    # buffer cell
    lib.add('asic', 'cells', 'buf', ['sky130_fd_sc_hd__buf_4/A/X'])

    # tie cells
    lib.add('asic', 'cells', 'tie', ['sky130_fd_sc_hd__conb_1/HI',
                                      'sky130_fd_sc_hd__conb_1/LO'])

    # Defaults for OpenROAD tool variables
    lib.set('asic', 'var', 'openroad', 'place_density', ['0.6'])
    lib.set('asic', 'var', 'openroad', 'pad_global_place', ['4'])
    lib.set('asic', 'var', 'openroad', 'pad_detail_place', ['2'])
    lib.set('asic', 'var', 'openroad', 'macro_place_halo', ['1', '1'])
    lib.set('asic', 'var', 'openroad', 'macro_place_channel', ['80', '80'])

    # Yosys techmap
    lib.add('asic', 'file', 'yosys', 'techmap',
             libdir + '/techmap/yosys/cells_latch.v')

    # Openroad specific files
    lib.set('asic', 'file', 'openroad', 'pdngen', libdir+'/apr/openroad/pdngen.tcl')
    lib.set('asic', 'file', 'openroad', 'global_connect', libdir+'/apr/openroad/global_connect.tcl')
    lib.set('asic', 'file', 'openroad', 'tapcells', libdir+'/apr/openroad/tapcell.tcl')

    chip.import_library(lib)

#########################
if __name__ == "__main__":

    lib = make_docs()
    lib.write_manifest('sky130.tcl')
