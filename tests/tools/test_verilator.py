# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.
import os
import pytest
import siliconcompiler
from siliconcompiler.targets import freepdk45_demo

@pytest.mark.eda
@pytest.mark.quick
def test_verilator(oh_dir):
    ydir = os.path.join(oh_dir, 'stdlib', 'hdl')

    design = "oh_fifo_sync"
    topfile = os.path.join(ydir, f'{design}.v')
    step = "import"

    chip = siliconcompiler.Chip(design)
    chip.input(topfile)
    chip.set('option', 'ydir', ydir)
    chip.set('option', 'relax', True)
    chip.set('option', 'quiet', True)
    chip.set('option', 'mode', 'sim')
    chip.node('verilator', step, 'verilator', step)
    chip.use(freepdk45_demo)
    chip.set('option', 'flow', 'verilator')
    chip.run()

    # check that compilation succeeded
    assert chip.find_result('v', step=step) is not None

#########################
if __name__ == "__main__":
    oh_dir = os.path.join('third_party', 'designs', 'oh')
    test_verilator(oh_dir)
