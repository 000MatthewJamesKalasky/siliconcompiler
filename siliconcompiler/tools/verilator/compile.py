import subprocess

from siliconcompiler.tools.verilator.verilator import setup as setup_tool

def setup(chip):
    ''' Helper method to load configs specific to compile tasks.
    '''

    # Generic tool setup.
    setup_tool(chip)

    tool = 'verilator'
    step = chip.get('arg','step')
    index = chip.get('arg','index')
    task = 'compile'
    design = chip.top()

    chip.add('tool', tool, 'task', task, 'option',  ['--cc', '--exe'], step=step, index=index)
    chip.set('tool', tool, 'task', task, 'input', f'{design}.v', step=step, index=index)
    chip.add('tool', tool, 'task', task, 'option', f'-o ../outputs/{design}.vexe', step=step, index=index)

def post_process(chip):
    ''' Tool specific function to run after step execution
    '''

    design = chip.top()
    step = chip.get('arg','step')

    # Run make to compile Verilated design into executable.
    # If we upgrade our minimum supported Verilog, we can remove this and
    # use the --build flag instead.
    proc = subprocess.run(['make', '-C', 'obj_dir', '-f', f'V{design}.mk'])
    if proc.returncode > 0:
        chip.error(
            f'Make returned error code {proc.returncode} when compiling '
            'Verilated design', fatal=True
        )