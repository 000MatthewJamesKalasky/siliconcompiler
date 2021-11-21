# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.

#Standard Modules
import sys
import logging
import os
import re
import json
import sys
import uuid
from multiprocessing import Process

#Shorten siliconcompiler as sc
import siliconcompiler
import siliconcompiler.client

###########################
def main():


    progname = "sc"
    description = """
    ------------------------------------------------------------
    SiliconCompiler is an open source compiler framework that
    aims to enable automated translation from source code to
    silicon.

    The sc program includes the followins steps.

    1. Read command line arguments
    2. If not set, 'design' is set to base of first source file.
    3. If not set, 'target' is set to 'asicflow_freepdk45.
    4. Run compilation
    5. Display summary

    Sources: https://github.com/siliconcompiler/siliconcompiler
    ------------------------------------------------------------
    """

    # Create a base chip class.
    chip = siliconcompiler.Chip()

    # Read command-line inputs and generate Chip objects to run the flow on.
    chip.create_cmdline(progname,
                        description=description)

    # Set design if none specified
    if not chip.get('design'):
        topfile = chip.get('source')[0]
        topmodule = os.path.splitext(os.path.basename(topfile))[0]
        chip.set('design', topmodule)

    # Set target if none specified
    if not chip.get('target'):
        chip.target('asicflow_freepdk45')

    # Run flow
    chip.run()

    # Print Job Summary
    chip.summary()

#########################
if __name__ == "__main__":

    sys.exit(main())
