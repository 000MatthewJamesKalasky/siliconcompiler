import siliconcompiler
import pytest

from siliconcompiler.pdks import asap7, freepdk45, skywater130
from siliconcompiler.fpgas import vpr_example
from siliconcompiler.targets import fpgaflow_demo


def test_target_valid():
    '''Basic test of target function.'''
    chip = siliconcompiler.Chip('test')
    chip.load_target("freepdk45_demo")

    assert chip.get('option', 'mode') == 'asic'


def test_target_fpga_valid():
    '''Ensure that the VPR FPGA flow allows legal part names and sets mode
    correctly.'''
    chip = siliconcompiler.Chip('test')
    chip.set('option', 'fpga', 'example_arch_X005_Y005')
    chip.load_target(fpgaflow_demo)

    assert chip.get('option', 'mode') == 'fpga'


@pytest.mark.parametrize('pdk', [asap7, freepdk45, skywater130])
def test_pdk(pdk):
    name = pdk.__name__.split('.')[-1]
    chip = siliconcompiler.Chip('test')
    chip.use(pdk)
    assert chip.getkeys('pdk')[0] == name
