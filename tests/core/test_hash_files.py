# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.
import os
import siliconcompiler
from siliconcompiler.targets import freepdk45_demo

def test_hash_files():
    chip = siliconcompiler.Chip('top')

    chip.use(freepdk45_demo)
    chip.write_manifest("raw.json")
    allkeys = chip.allkeys()
    for keypath in allkeys:
        if 'file' in chip.get(*keypath, field='type'):
            chip.hash_files(*keypath)
    chip.write_manifest("hashed.json")

#########################
if __name__ == "__main__":
    test_hash_files()
