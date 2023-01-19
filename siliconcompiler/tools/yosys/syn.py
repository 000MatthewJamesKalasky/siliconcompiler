
from .yosys import setup as setup_tool

def setup(chip):
    ''' Helper method for configs specific to synthesis tasks.
    '''

    # Generic tool setup.
    setup_tool(chip)

    tool = 'yosys'
    task = 'syn'
    step = chip.get('arg','step')
    index = chip.get('arg','index')
    design = chip.top()

    # Set yosys script path.
    chip.set('tool', tool, 'task', task, 'script', step, index, 'sc_syn.tcl', clobber=False)

    # Input/output requirements.
    chip.set('tool', tool, 'task', task, 'input', step, index, design + '.v')
    chip.set('tool', tool, 'task', task, 'output', step, index, design + '.vg')
    chip.add('tool', tool, 'task', task, 'output', step, index, design + '_netlist.json')
    chip.add('tool', tool, 'task', task, 'output', step, index, design + '.blif')
