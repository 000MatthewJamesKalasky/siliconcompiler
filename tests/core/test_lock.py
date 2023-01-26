# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.
import siliconcompiler
from siliconcompiler.targets import freepdk45_demo

##################################
def test_lock():
    '''API test for show method
    '''

    # Create instance of Chip class
    chip = siliconcompiler.Chip('gcd')
    chip.use(freepdk45_demo)
    chip.set('design', True, field="lock")
    chip.set('design', "FAIL")

    assert (chip.get('design') == "gcd")

#########################
if __name__ == "__main__":
    test_lock()
