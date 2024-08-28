import os
import siliconcompiler
from siliconcompiler import NodeStatus
from siliconcompiler.flowgraph import _get_flowgraph_nodes
import pytest

from siliconcompiler.targets import freepdk45_demo


@pytest.fixture
def chip():
    chip = siliconcompiler.Chip('test')
    chip.use(freepdk45_demo)

    for step, index in _get_flowgraph_nodes(chip, 'asicflow'):
        chip.set('record', 'status', NodeStatus.SUCCESS, step=step, index=index)

    return chip


def test_checklist(chip):
    '''API test for help method
    '''

    # Test won't work if file doesn't exist
    os.makedirs('build/test/job0/syn/0')
    with open('build/test/job0/syn/0/yosys.log', 'w') as f:
        f.write('test')

    chip.set('metric', 'errors', 1, step='syn', index='0')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'report', 'errors', 'yosys.log',
             step='syn', index='0')
    chip.schema.record_history()

    # automated fail
    chip.set('checklist', 'iso', 'd0', 'criteria', 'errors==0')
    chip.set('checklist', 'iso', 'd0', 'task', ('job0', 'syn', '0'))
    assert not chip.check_checklist('iso', ['d0'])

    # automated pass
    chip.set('checklist', 'iso', 'd1', 'criteria', 'errors<2')
    chip.set('checklist', 'iso', 'd1', 'task', ('job0', 'syn', '0'))
    assert chip.check_checklist('iso', ['d1'])

    assert not chip.check_checklist('iso', ['d1'], check_ok=True)

    chip.set('checklist', 'iso', 'd1', 'ok', True)
    assert chip.check_checklist('iso', ['d1'], check_ok=True)


def test_checklist_no_reports(chip):
    '''API test for help method
    '''

    chip.set('metric', 'errors', 1, step='syn', index='0')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'report', 'errors', 'yosys.log',
             step='syn', index='0')
    chip.schema.record_history()

    # automated pass
    chip.set('checklist', 'iso', 'd1', 'criteria', 'errors<2')
    chip.set('checklist', 'iso', 'd1', 'task', ('job0', 'syn', '0'))
    assert chip.check_checklist('iso', ['d1'], require_reports=False)


def test_checklist_changed_flow(chip):
    '''API test for help method
    '''

    chip.set('metric', 'errors', 1, step='syn', index='0')
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'report', 'errors', 'yosys.log',
             step='syn', index='0')
    chip.schema.record_history()

    chip.set('option', 'flow', 'lintflow')

    # automated pass
    chip.set('checklist', 'iso', 'd1', 'criteria', 'errors<2')
    chip.set('checklist', 'iso', 'd1', 'task', ('job0', 'syn', '0'))
    assert chip.check_checklist('iso', ['d1'], require_reports=False)


def test_checklist_no_non_logged_keys(chip):
    metrics = (
        'tasktime',
        'exetime',
        'memory'
    )

    for metric in metrics:
        chip.set('metric', metric, 10, step='syn', index='0')
    chip.schema.record_history()

    for metric in metrics:
        chip.add('checklist', 'iso', 'd0', 'criteria', f'{metric}==10')
    chip.set('checklist', 'iso', 'd0', 'task', ('job0', 'syn', '0'))
    assert chip.check_checklist('iso', ['d0'])


def test_missing_check_checklist(chip):
    '''
    Check that check_checklist will generate an error on missing items
    '''

    # automated fail
    chip.set('checklist', 'iso', 'd1', 'criteria', 'errors==0')
    chip.set('checklist', 'iso', 'd1', 'task', ('job0', 'syn', '0'))
    assert not chip.check_checklist('iso', ['d0'])


def test_missing_job(chip):
    '''
    Check that check_checklist will generate an error on missing jobs
    '''

    # automated fail
    chip.set('checklist', 'iso', 'd0', 'criteria', 'errors==0')
    chip.set('checklist', 'iso', 'd0', 'task', ('job1', 'syn', '0'))
    with pytest.raises(siliconcompiler.SiliconCompilerError):
        chip.check_checklist('iso', ['d0'])


def test_missing_step(chip):
    '''
    Check that check_checklist will generate an error on missing steps
    '''

    chip.schema.record_history()

    # automated fail
    chip.set('checklist', 'iso', 'd0', 'criteria', 'errors==0')
    chip.set('checklist', 'iso', 'd0', 'task', ('job0', 'synth', '0'))
    with pytest.raises(siliconcompiler.SiliconCompilerError, match='synth not found in flowgraph'):
        chip.check_checklist('iso', ['d0'])


def test_missing_index(chip):
    '''
    Check that check_checklist will generate an error on missing indexes
    '''

    chip.schema.record_history()

    # automated fail
    chip.set('checklist', 'iso', 'd0', 'criteria', 'errors==0')
    chip.set('checklist', 'iso', 'd0', 'task', ('job0', 'syn', '1'))
    with pytest.raises(siliconcompiler.SiliconCompilerError, match='syn1 not found in flowgraph'):
        chip.check_checklist('iso', ['d0'])


def test_missing_checklist(chip):
    '''
    Check if check_checklist fails when checklist has not been loaded.
    '''

    assert not chip.check_checklist('iso')


def test_criteria_formatting_float_pass(chip):
    # Test won't work if file doesn't exist
    os.makedirs('build/test/job0/syn/0')
    with open('build/test/job0/syn/0/yosys.log', 'w') as f:
        f.write('test')

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'report', 'fmax', 'yosys.log',
             step='syn', index='0')
    chip.set('checklist', 'iso', 'd0', 'task', ('job0', 'syn', '0'))

    for criteria in (
        '1.0',
        '+1.0',
        '-1.0',
        '1.0e+09',
        '1.0e-09',
        '1.0e-9',
        ' 1.0e-9 ',
    ):
        chip.set('metric', 'fmax', criteria.strip(), step='syn', index='0')
        chip.schema.record_history()
        chip.set('checklist', 'iso', 'd0', 'criteria', f'fmax=={criteria}')

        assert chip.check_checklist('iso', ['d0'])


def test_criteria_formatting_float_fail(chip):
    chip.set('checklist', 'iso', 'd0', 'task', ('job0', 'syn', '0'))

    for criteria in (
        '1.0.0',
        '+ 1.0',
        '1.0e+09.5',
        '1.0 e-09',
        '1.0e -9',
    ):
        chip.set('metric', 'fmax', 5, step='syn', index='0')
        chip.schema.record_history()
        chip.set('checklist', 'iso', 'd0', 'criteria', f'fmax=={criteria}')

        with pytest.raises(siliconcompiler.SiliconCompilerError):
            assert not chip.check_checklist('iso', ['d0'])


#########################
if __name__ == "__main__":
    test_checklist()
