import os
import siliconcompiler

import pytest

@pytest.fixture
def chip(datadir):
    # Create instance of Chip class
    chip = siliconcompiler.Chip('bad', loglevel='NOTSET')

    # Inserting value into configuration
    chip.input(os.path.join(datadir, 'bad.v'))
    chip.set('design', 'bad')
    chip.set('constraint', 'outline', [(0, 0), (10, 10)])
    chip.set('constraint', 'corearea', [(1, 1), (9, 9)])
    chip.load_target("freepdk45_demo")

    chip.add('option', 'steplist', 'import')
    chip.add('option', 'steplist', 'syn')

    return chip

@pytest.mark.eda
def test_failure_notquiet(chip):
    '''Test that SC exits early on errors without -quiet switch.

    This is a regression test for an issue where SC would only exit early on a
    command failure in cases where the -quiet switch was included.

    TODO: these tests are somewhat bad because unrelated failures can cause
    them to pass. Needs a more specific check.
    '''

    # Expect that command exits early
    with pytest.raises(siliconcompiler.SiliconCompilerError):
        chip.run()

    # Check we made it past initial setup
    assert os.path.isdir('build/bad/job0/import')
    assert os.path.isdir('build/bad/job0/syn')

    # Expect that there is no import output
    assert chip.find_result('v', step='import') is None
    # Expect that synthesis doesn't run
    assert not os.path.isdir('build/bad/job0/syn/0/syn.log')

@pytest.mark.eda
def test_failure_quiet(chip):
    '''Test that SC exits early on errors with -quiet switch.
    '''

    chip.set('option', 'quiet', True)

    # Expect that command exits early
    with pytest.raises(siliconcompiler.SiliconCompilerError):
        chip.run()

    # Check we made it past initial setup
    assert os.path.isdir('build/bad/job0/import')
    assert os.path.isdir('build/bad/job0/syn')

    # Expect that there is no import output
    assert chip.find_result('v', step='import') is None
    # Expect that synthesis doesn't run
    assert not os.path.isdir('build/bad/job0/syn/0/syn.log')

@pytest.mark.quick
def test_incomplete_flowgraph():
    '''Test that SC exits early when flowgraph is incomplete
    '''

    chip = siliconcompiler.Chip('gcd')
    chip.load_target("freepdk45_demo")

    flow = chip.get('option', 'flow')

    chip.edge(flow, 'export', 'dummy_step')

    # Expect that command exits early
    try:
        chip.run()
    except siliconcompiler.SiliconCompilerError as e:
        assert str(e).startswith(flow)
    else:
        assert False
