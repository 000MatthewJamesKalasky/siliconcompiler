import siliconcompiler
from siliconcompiler.tools.klayout.klayout import setup as setup_tool
from siliconcompiler.tools.klayout.show import find_incoming_ext

def make_docs():
    chip = siliconcompiler.Chip('<design>')
    chip.load_target('freepdk45_demo')
    step = 'screenshot'
    index = '<index>'
    chip.set('arg','step',step)
    chip.set('arg','index',index)
    chip.set('flowgraph', chip.get('option', 'flow'), step, index, 'task', 'screenshot')
    chip.set('tool', 'klayout', 'task', 'screenshot', 'var', 'show_filepath', '<path>')
    setup(chip)

    return chip

def setup(chip):
    ''' Helper method for configs specific to screenshot tasks.
    '''

    # Generic tool setup.
    setup_tool(chip)

    tool = 'klayout'
    refdir = 'tools/'+tool
    step = chip.get('arg','step')
    index = chip.get('arg','index')
    design = chip.top()
    task = 'screenshot'
    clobber = False

    script = 'klayout_show.py'
    option = ['-nc', '-z', '-rm']
    chip.set('tool', tool, 'task', task, 'script', script, step=step, index=index, clobber=clobber)
    chip.set('tool', tool, 'task', task, 'option', option, step=step, index=index, clobber=clobber)

    pdk = chip.get('option', 'pdk')
    stackup = chip.get('option', 'stackup')
    if chip.valid('pdk', pdk, 'var', 'klayout', 'hide_layers', stackup):
        layers_to_hide = chip.get('pdk', pdk, 'var', 'klayout', 'hide_layers', stackup)
        chip.add('tool', tool, 'task', task, 'var', 'hide_layers', layers_to_hide, step=step, index=index)
    if chip.valid('tool', tool, 'task', task, 'var', 'show_filepath'):
        chip.add('tool', tool, 'task', task, 'require', ",".join(['tool', tool, 'task', task, 'var', 'show_filepath']), step=step, index=index)
    else:
        incoming_ext = find_incoming_ext(chip)
        chip.add('tool', tool, 'task', task, 'require', ",".join(['tool', tool, 'task', task, 'var', 'show_filetype']), step=step, index=index)
        chip.set('tool', tool, 'task', task, 'var', 'show_filetype', incoming_ext, step=step, index=index)
        chip.add('tool', tool, 'task', task, 'input', f'{design}.{incoming_ext}', step=step, index=index)
    chip.set('tool', tool, 'task', task, 'var', 'show_exit', "true", step=step, index=index, clobber=False)

    chip.add('tool', tool, 'task', task, 'output', design + '.png', step=step, index=index)
    chip.set('tool', tool, 'task', task, 'var', 'show_horizontal_resolution', '1024', step=step, index=index, clobber=False)
    chip.set('tool', tool, 'task', task, 'var', 'show_vertical_resolution', '1024', step=step, index=index, clobber=False)