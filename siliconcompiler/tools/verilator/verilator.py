import os
import subprocess

import siliconcompiler

####################################################################
# Make Docs
####################################################################

def make_docs():
    '''
    Verilator is a free and open-source software tool which converts Verilog (a
    hardware description language) to a cycle-accurate behavioral model in C++
    or SystemC.

    Steps supported
    ---------------

    **import**

    Preprocesses and pickles Verilog sources. Takes in a set of Verilog source
    files supplied via :keypath:`input, verilog` and reads the following
    parameters:

    * :keypath:`option, ydir`
    * :keypath:`option, vlib`
    * :keypath:`option, idir`
    * :keypath:`option, cmdfile`

    Outputs a single Verilog file in ``outputs/<design>.v``.

    **lint**

    Lints Verilog source. Takes in a single pickled Verilog file from
    ``inputs/<design>.v`` and produces no outputs. Results of linting can be
    programatically queried using errors/warnings metrics.

    **compile**

    Compiles Verilog and C/C++ sources into an executable.  Takes in a single
    pickled Verilog file from ``inputs/<design>.v`` and a set of C/C++ sources
    from :keypath:`input, c`. Outputs an executable in
    ``outputs/<design>.vexe``.

    This step supports using the :keypath:`option, trace` parameter to enable
    Verilator's ``--trace`` flag.

    For all steps, this driver runs Verilator using the ``-sv`` switch to enable
    parsing a subset of SystemVerilog features. All steps also support using
    :keypath:`option, relax` to make warnings nonfatal.

    Documentation: https://verilator.org/guide/latest

    Sources: https://github.com/verilator/verilator

    Installation: https://verilator.org/guide/latest/install.html

    '''

    chip = siliconcompiler.Chip('<design>')
    chip.set('arg','step','import')
    chip.set('arg','index','<index>')
    setup(chip)
    return chip

def setup(chip):
    ''' Per tool function that returns a dynamic options string based on
    the dictionary settings. Static setings only.
    '''

    tool = 'verilator'
    step = chip.get('arg','step')
    index = chip.get('arg','index')
    task = chip.get_task(step, index)
    design = chip.top()

    # Basic Tool Setup
    chip.set('tool', tool, 'exe', 'verilator')
    chip.set('tool', tool, 'vswitch', '--version')
    chip.set('tool', tool, 'version', '>=4.028', clobber=False)

    # Common to all tasks
    # Max threads
    chip.set('tool', tool, 'task', task, 'threads', step, index,  os.cpu_count(), clobber=False)

    # Basic warning and error grep check on logfile
    chip.set('tool', tool, 'task', task, 'regex', step, index, 'warnings', r"^\%Warning", clobber=False)
    chip.set('tool', tool, 'task', task, 'regex', step, index, 'errors', r"^\%Error", clobber=False)

    # Generic CLI options (for all steps)
    chip.set('tool', tool, 'task', task, 'option', step, index,  '-sv')
    chip.add('tool', tool, 'task', task, 'option', step, index, f'--top-module {design}')

    # Make warnings non-fatal in relaxed mode
    if chip.get('option', 'relax'):
        chip.add('tool', tool, 'task', task, 'option', step, index, ['-Wno-fatal', '-Wno-UNOPTFLAT'])

    # Converting user setting to verilator specific filter
    #for warning in chip.get('tool', tool, 'task', task, step, index, 'warningoff'):
    #    chip.add('tool', tool, 'task', task, 'option', step, index, f'-Wno-{warning}')

    # User runtime option
    if chip.get('option', 'trace'):
        chip.add('tool', tool, 'task', task, 'task', task, 'option', step, index, '--trace')

################################
#  Custom runtime options
################################

def runtime_options(chip):
    '''
    CLI options that involve filepaths (must be resolved at runtime, in case
    we're running on a different machine than client).
    '''
    cmdlist = []
    step = chip.get('arg', 'step')

    if step == 'import':
        for value in chip.find_files('option', 'ydir'):
            cmdlist.append('-y ' + value)
        for value in chip.find_files('option', 'vlib'):
            cmdlist.append('-v ' + value)
        for value in chip.find_files('option', 'idir'):
            cmdlist.append('-I' + value)
        for value in chip.find_files('option', 'cmdfile'):
            cmdlist.append('-f ' + value)
        for value in chip.find_files('input', 'rtl', 'verilog'):
            cmdlist.append(value)
    elif step == 'compile':
        for value in chip.find_files('input', 'hll', 'c'):
            cmdlist.append(value)

    return cmdlist

################################
# Version Check
################################

def parse_version(stdout):
    # Verilator 4.104 2020-11-14 rev v4.104
    return stdout.split()[1]

################################
# Post_process (post executable)
################################

def post_process(chip):
    ''' Tool specific function to run after step execution
    '''

    design = chip.top()
    step = chip.get('arg','step')

    if step == 'import':
        # Post-process hack to collect vpp files
        # Creating single file "pickle' synthesis handoff
        subprocess.run('egrep -h -v "\\`begin_keywords" obj_dir/*.vpp > verilator.v',
                       shell=True)

        # Moving pickled file to outputs
        os.rename("verilator.v", f"outputs/{design}.v")
    elif step == 'compile':
        # Run make to compile Verilated design into executable.
        # If we upgrade our minimum supported Verilog, we can remove this and
        # use the --build flag instead.
        proc = subprocess.run(['make', '-C', 'obj_dir', '-f', f'V{design}.mk'])
        if proc.returncode > 0:
            chip.error(
                f'Make returned error code {proc.returncode} when compiling '
                'Verilated design', fatal=True
            )

##################################################
if __name__ == "__main__":

    chip = make_docs()
    chip.write_manifest("verilator.csv")
