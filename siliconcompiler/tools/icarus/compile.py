import os

def setup(chip):
    ''' Per tool function that returns a dynamic options string based on
    the dictionary settings.
    '''

    # If the 'lock' bit is set, don't reconfigure.
    tool = 'icarus'
    task = 'compile'
    step = chip.get('arg','step')
    index = chip.get('arg','index')
    design = chip.top()

    # Standard Setup
    chip.set('tool', tool, 'exe', 'iverilog')
    chip.set('tool', tool, 'vswitch', '-V')
    chip.set('tool', tool, 'version', '>=10.3', clobber=False)

    # Only one task (compile)
    chip.add('tool', tool, 'task', task, 'require', 'input,rtl,verilog', step=step, index=index)
    chip.set('tool', tool, 'task', task, 'option', '-o outputs/'+design+'.vvp', step=step, index=index)
    chip.set('tool', tool, 'task', task, 'threads', os.cpu_count(), step=step, index=index, clobber=False)