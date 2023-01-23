import os
import siliconcompiler

def make_docs():
    '''
    ASAP 7 7.5-track standard cell library.
    '''
    chip =  siliconcompiler.Chip('<design>')
    setup(chip)
    return chip

def _setup_lib(libname, suffix):
    lib = siliconcompiler.Chip(libname)

    group = 'asap7sc7p5t'
    vt = 'rvt'
    libname = f'{group}_{vt}'
    foundry = 'virtual'
    process = 'asap7'
    stackup = '10M'
    libtype = '7p5t'
    rev = 'r1p7'
    corner = 'typical'
    objectives = ['setup']

    libdir = os.path.join('..', 'third_party', 'pdks', foundry, process, 'libs', libname, rev)

    # rev
    lib.set('package', 'version',rev)

    # todo: remove later
    lib.set('option', 'pdk', 'asap7')

    # timing
    lib.add('output', corner, 'nldm', libdir+'/nldm/'+libname+'_ff.lib')

    # lef
    lib.add('output', stackup, 'lef', libdir+'/lef/'+libname+'.lef')

    # gds
    lib.add('output', stackup, 'gds', libdir+'/gds/'+libname+'.gds')

    # site name
    lib.set('asic', 'footprint', 'asap7sc7p5t', 'symmetry', 'Y')
    lib.set('asic', 'footprint', 'asap7sc7p5t', 'size', (0.054,0.270))

    # lib arch
    lib.set('asic', 'libarch', libtype)

    #default input driver
    lib.add('asic', 'cells', 'driver', f"BUFx2_ASAP7_75t_{suffix}")

    # clock buffers
    lib.add('asic', 'cells', 'clkbuf', f"BUFx2_ASAP7_75t_{suffix}")

    # tie cells
    lib.add('asic', 'cells', 'tie', [f"TIEHIx1_ASAP7_75t_{suffix}/H",
                                     f"TIELOx1_ASAP7_75t_{suffix}/L"])

    # buffer
    # TODO: Need to fix this syntax!, not needed by modern tools!
    lib.add('asic', 'cells', 'buf', [f"BUFx2_ASAP7_75t_{suffix}/A/Y"])

    # hold cells
    lib.add('asic', 'cells', 'hold', f"BUFx2_ASAP7_75t_{suffix}")

    # filler
    lib.add('asic', 'cells', 'filler', [f"FILLER_ASAP7_75t_{suffix}"])

    # Stupid small cells
    lib.add('asic', 'cells', 'dontuse', ["*x1_ASAP7*",
                                         "*x1p*_ASAP7*",
                                         "*xp*_ASAP7*",
                                         "SDF*",
                                         "ICG*",
                                         "DFFH*"])

    # Tapcell
    lib.add('asic', 'cells', 'tap', f"TAPCELL_ASAP7_75t_{suffix}")

    # Endcap
    lib.add('asic', 'cells','endcap', f"DECAPx1_ASAP7_75t_{suffix}")

    # Yosys techmap
    if libname.endswith('rvt'):
        # TODO: write map files for other groups
        lib.add('asic', 'file', 'yosys', 'techmap',
                    libdir + '/techmap/yosys/cells_latch.v')

    # Defaults for OpenROAD tool variables
    lib.set('asic', 'var', 'openroad', 'place_density', ['0.77'])
    lib.set('asic', 'var', 'openroad', 'pad_global_place', ['2'])
    lib.set('asic', 'var', 'openroad', 'pad_detail_place', ['1'])
    lib.set('asic', 'var', 'openroad', 'macro_place_halo', ['22.4', '15.12'])
    lib.set('asic', 'var', 'openroad', 'macro_place_channel', ['18.8', '19.95'])

    # Openroad APR setup files
    lib.set('asic', 'file', 'openroad', 'tracks', libdir + '/apr/openroad/tracks.tcl')
    lib.set('asic', 'file', 'openroad', 'tapcells', libdir + '/apr/openroad/tapcells.tcl')
    lib.set('asic', 'file', 'openroad', 'pdngen', libdir + '/apr/openroad/pdngen.tcl')
    lib.set('asic', 'file', 'openroad', 'global_connect', libdir + '/apr/openroad/global_connect.tcl')

    return lib

def setup(chip):
    all_libs = {
        'asap7sc7p5t_rvt' : 'R',
        'asap7sc7p5t_lvt' : 'L',
        'asap7sc7p5t_slvt' : 'SL'
    }

    for libname, suffix in all_libs.items():
        lib = _setup_lib(libname, suffix)
        chip.import_library(lib)
