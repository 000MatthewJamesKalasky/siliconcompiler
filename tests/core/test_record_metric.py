# Copyright 2023 Silicon Compiler Authors. All Rights Reserved.
import pytest
import siliconcompiler
from siliconcompiler.scheduler import _clear_metric
from siliconcompiler.tools._common import record_metric
from siliconcompiler.targets import freepdk45_demo


@pytest.fixture
def chip():
    # Create instance of Chip class
    chip = siliconcompiler.Chip('test')
    chip.use(freepdk45_demo)

    return chip


def test_metric_with_units(chip):
    record_metric(chip, 'floorplan', '0', 'peakpower', 1.05e6, None, source_unit='uW')
    assert chip.get('metric', 'peakpower',
                    step='floorplan', index='0') == 1.05e3

    flow = chip.get('option', 'flow')
    tool = chip.get('flowgraph', flow, 'floorplan', '0', 'tool')
    task = chip.get('flowgraph', flow, 'floorplan', '0', 'task')
    assert chip.get('tool', tool, 'task', task, 'report', 'peakpower',
                    step='floorplan', index='0') == []


def test_metric_without_units(chip):
    record_metric(chip, 'floorplan', '0', 'cells', 25, None)
    assert chip.get('metric', 'cells',
                    step='floorplan', index='0') == 25

    flow = chip.get('option', 'flow')
    tool = chip.get('flowgraph', flow, 'floorplan', '0', 'tool')
    task = chip.get('flowgraph', flow, 'floorplan', '0', 'task')
    assert chip.get('tool', tool, 'task', task, 'report', 'cells',
                    step='floorplan', index='0') == []


def test_metric_with_source(chip):
    record_metric(chip, 'floorplan', '0', 'cells', 25, 'report.txt')
    assert chip.get('metric', 'cells',
                    step='floorplan', index='0') == 25

    flow = chip.get('option', 'flow')
    tool = chip.get('flowgraph', flow, 'floorplan', '0', 'tool')
    task = chip.get('flowgraph', flow, 'floorplan', '0', 'task')
    assert chip.get('tool', tool, 'task', task, 'report', 'cells',
                    step='floorplan', index='0') == ['report.txt']


def test_metric_clear(chip):
    record_metric(chip, 'floorplan', '0', 'cells', 25, 'report.txt')
    assert chip.get('metric', 'cells',
                    step='floorplan', index='0') == 25

    flow = chip.get('option', 'flow')
    tool = chip.get('flowgraph', flow, 'floorplan', '0', 'tool')
    task = chip.get('flowgraph', flow, 'floorplan', '0', 'task')
    assert chip.get('tool', tool, 'task', task, 'report', 'cells',
                    step='floorplan', index='0') == ['report.txt']

    _clear_metric(chip, 'floorplan', '0', 'cells')
    assert chip.get('metric', 'cells', step='floorplan', index='0') is None
    assert chip.get('tool', tool, 'task', task, 'report', 'cells',
                    step='floorplan', index='0') == []
