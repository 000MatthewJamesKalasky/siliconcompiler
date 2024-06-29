import siliconcompiler
from siliconcompiler.flowgraph import gather_resume_failed_nodes
from siliconcompiler.scheduler import _setup_workdir
from siliconcompiler import NodeStatus

import os
import pytest
import shutil
from pathlib import Path


@pytest.mark.eda
@pytest.mark.timeout(600)
def test_resume(gcd_chip):
    # Set a value that will cause place to break
    gcd_chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', 'asdf',
                 step='place', index='0')

    gcd_chip.set('option', 'to', 'cts')

    with pytest.raises(siliconcompiler.SiliconCompilerError):
        gcd_chip.run()

    # Ensure flow failed at placement, and store last modified time of floorplan
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    old_fp_mtime = os.path.getmtime(fp_result)

    assert gcd_chip.find_result('def', step='place') is None
    assert gcd_chip.find_result('def', step='cts') is None

    # Fix place step and re-run
    gcd_chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.40',
                 step='place', index='0')
    gcd_chip.set('option', 'resume', True)
    gcd_chip.run()

    # Ensure floorplan did not get re-run
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    assert os.path.getmtime(fp_result) == old_fp_mtime

    # Ensure flow finished successfully
    assert gcd_chip.find_result('def', step='place') is not None
    assert gcd_chip.find_result('def', step='cts') is not None


def test_resume_with_missing_node_missing_node(gcd_chip):
    flow = gcd_chip.get('option', 'flow')
    for step, index in gcd_chip.nodes_to_execute():
        _setup_workdir(gcd_chip, step, index, False)

        gcd_chip.set('flowgraph', flow, step, index, 'status', NodeStatus.SUCCESS)

        cfg = f"{gcd_chip._getworkdir(step=step, index=index)}/outputs/{gcd_chip.design}.pkg.json"
        gcd_chip.write_manifest(cfg)

    shutil.rmtree(gcd_chip._getworkdir(step='place', index='0'))

    gcd_chip.set('option', 'resume', True)

    resume_nodes = gather_resume_failed_nodes(
        gcd_chip,
        gcd_chip.get('option', 'flow'),
        gcd_chip.nodes_to_execute())
    assert ('import', '0') not in resume_nodes
    assert ('syn', '0') not in resume_nodes
    assert ('floorplan', '0') not in resume_nodes
    assert ('place', '0') in resume_nodes
    assert ('cts', '0') in resume_nodes
    assert ('route', '0') in resume_nodes
    assert ('dfm', '0') in resume_nodes
    assert ('write_gds', '0') in resume_nodes
    assert ('write_data', '0') in resume_nodes


def test_resume_with_missing_node_failed_node(gcd_chip):
    flow = gcd_chip.get('option', 'flow')
    for step, index in gcd_chip.nodes_to_execute():
        _setup_workdir(gcd_chip, step, index, False)

        if step == 'place':
            gcd_chip.set('flowgraph', flow, step, index, 'status', NodeStatus.ERROR)
        else:
            gcd_chip.set('flowgraph', flow, step, index, 'status', NodeStatus.SUCCESS)

        cfg = f"{gcd_chip._getworkdir(step=step, index=index)}/outputs/{gcd_chip.design}.pkg.json"
        gcd_chip.write_manifest(cfg)

    gcd_chip.set('option', 'resume', True)

    resume_nodes = gather_resume_failed_nodes(
        gcd_chip,
        gcd_chip.get('option', 'flow'),
        gcd_chip.nodes_to_execute())
    assert ('import', '0') not in resume_nodes
    assert ('syn', '0') not in resume_nodes
    assert ('floorplan', '0') not in resume_nodes
    assert ('place', '0') in resume_nodes
    assert ('cts', '0') in resume_nodes
    assert ('route', '0') in resume_nodes
    assert ('dfm', '0') in resume_nodes
    assert ('write_gds', '0') in resume_nodes
    assert ('write_data', '0') in resume_nodes


def test_resume_with_missing_node_no_failures(gcd_chip):
    flow = gcd_chip.get('option', 'flow')
    for step, index in gcd_chip.nodes_to_execute():
        _setup_workdir(gcd_chip, step, index, False)

        gcd_chip.set('flowgraph', flow, step, index, 'status', NodeStatus.SUCCESS)

        cfg = f"{gcd_chip._getworkdir(step=step, index=index)}/outputs/{gcd_chip.design}.pkg.json"
        gcd_chip.write_manifest(cfg)

    gcd_chip.set('option', 'resume', True)

    resume_nodes = gather_resume_failed_nodes(
        gcd_chip,
        gcd_chip.get('option', 'flow'),
        gcd_chip.nodes_to_execute())
    assert len(resume_nodes) == 0


@pytest.mark.eda
@pytest.mark.timeout(600)
def test_resume_changed_value(gcd_chip):
    # Set a value that will cause place to break
    gcd_chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.20',
                 step='place', index='0')

    gcd_chip.set('option', 'to', 'cts')

    gcd_chip.run()

    # Ensure flow failed at placement, and store last modified time of floorplan
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    old_fp_mtime = os.path.getmtime(fp_result)
    pl_result = gcd_chip.find_result('def', step='place')
    assert pl_result is not None
    old_pl_mtime = os.path.getmtime(pl_result)

    assert gcd_chip.find_result('def', step='cts') is not None

    # Fix place step and re-run
    gcd_chip.set('tool', 'openroad', 'task', 'place', 'var', 'place_density', '0.40',
                 step='place', index='0')
    gcd_chip.set('option', 'resume', True)
    gcd_chip.run()

    # Ensure floorplan did not get re-run
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    assert os.path.getmtime(fp_result) == old_fp_mtime

    pl_result = gcd_chip.find_result('def', step='place')
    assert pl_result is not None
    assert os.path.getmtime(pl_result) != old_pl_mtime

    # Ensure flow finished successfully
    assert gcd_chip.find_result('def', step='place') is not None


@pytest.mark.eda
@pytest.mark.timeout(600)
def test_resume_changed_file_no_hash_no_changes(gcd_chip):
    gcd_chip.set('option', 'to', 'floorplan')

    gcd_chip.run()

    # Ensure flow failed at placement, and store last modified time of floorplan
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    old_im_result = os.path.getmtime(im_result)
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    old_fp_mtime = os.path.getmtime(fp_result)

    assert gcd_chip.find_result('def', step='cts') is None

    gcd_chip.set('option', 'resume', True)
    gcd_chip.run()

    # Ensure import did not re-run
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    assert os.path.getmtime(im_result) == old_im_result

    # Ensure floorplan did not re-run
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    assert os.path.getmtime(fp_result) == old_fp_mtime

    # Ensure flow finished successfully
    assert gcd_chip.find_result('def', step='place') is None


@pytest.mark.eda
@pytest.mark.timeout(600)
def test_resume_changed_file_no_hash_timestamp(gcd_chip):
    gcd_chip.set('option', 'to', 'floorplan')

    shutil.copyfile(
        gcd_chip.find_files('input', 'constraint', 'sdc', step='global', index='global')[0],
        './gcd.sdc')

    gcd_chip.set('input', 'constraint', 'sdc', './gcd.sdc')

    gcd_chip.run()

    # Ensure flow failed at placement, and store last modified time of floorplan
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    old_im_result = os.path.getmtime(im_result)
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    old_fp_mtime = os.path.getmtime(fp_result)

    assert gcd_chip.find_result('def', step='cts') is None

    # Change the timestamp on SDC file
    Path('./gcd.sdc').touch()
    gcd_chip.set('option', 'resume', True)
    gcd_chip.run()

    # Ensure import did not re-run
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    assert os.path.getmtime(im_result) == old_im_result

    # Ensure floorplan re-ran
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    assert os.path.getmtime(fp_result) != old_fp_mtime

    # Ensure flow finished successfully
    assert gcd_chip.find_result('def', step='place') is None


@pytest.mark.eda
@pytest.mark.timeout(600)
def test_resume_changed_file_no_hash_value_change(gcd_chip):
    gcd_chip.set('option', 'to', 'floorplan')

    # Copy file before to ensure timestamps are consistant
    shutil.copyfile(
        gcd_chip.find_files('input', 'constraint', 'sdc', step='global', index='global')[0],
        './gcd.sdc')

    gcd_chip.run()

    # Ensure flow failed at placement, and store last modified time of floorplan
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    old_im_result = os.path.getmtime(im_result)
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    old_fp_mtime = os.path.getmtime(fp_result)

    assert gcd_chip.find_result('def', step='cts') is None

    # Change the value of SDC
    gcd_chip.set('input', 'constraint', 'sdc', './gcd.sdc')

    gcd_chip.set('option', 'resume', True)
    gcd_chip.run()

    # Ensure import did not re-run
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    assert os.path.getmtime(im_result) == old_im_result

    # Ensure floorplan re-ran
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    assert os.path.getmtime(fp_result) != old_fp_mtime

    # Ensure flow finished successfully
    assert gcd_chip.find_result('def', step='place') is None


@pytest.mark.eda
@pytest.mark.timeout(600)
def test_resume_changed_file_with_hash(gcd_chip):
    gcd_chip.set('option', 'to', 'floorplan')
    gcd_chip.set('option', 'hash', True)

    gcd_chip.run()

    # Store last modified time of floorplan
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    old_im_result = os.path.getmtime(im_result)
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    old_fp_mtime = os.path.getmtime(fp_result)

    assert gcd_chip.find_result('def', step='cts') is None

    # File moved, but no changes
    shutil.copyfile(gcd_chip.find_files('input', 'rtl', 'verilog', step='import', index=0)[0],
                    './gcd.v')
    gcd_chip.set('input', 'rtl', 'verilog', './gcd.v')
    gcd_chip.set('option', 'resume', True)
    gcd_chip.run()

    # Ensure nothing re-ran
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    assert os.path.getmtime(im_result) == old_im_result

    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    assert os.path.getmtime(fp_result) == old_fp_mtime

    # Ensure flow finished successfully
    assert gcd_chip.find_result('def', step='place') is None


@pytest.mark.eda
@pytest.mark.timeout(600)
def test_resume_changed_file_with_hash_file_modify(gcd_chip):
    gcd_chip.set('option', 'to', 'floorplan')
    gcd_chip.set('option', 'hash', True)

    gcd_chip.run()

    # Ensure flow failed at placement, and store last modified time of floorplan
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    old_im_result = os.path.getmtime(im_result)
    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    old_fp_mtime = os.path.getmtime(fp_result)

    assert gcd_chip.find_result('def', step='cts') is None

    # File moved, and modified
    shutil.copyfile(gcd_chip.find_files('input', 'rtl', 'verilog', step='import', index=0)[0],
                    './gcd.v')
    with open('./gcd.v', 'a') as f:
        f.write('\n\n\n')
    gcd_chip.set('input', 'rtl', 'verilog', './gcd.v')
    gcd_chip.set('option', 'resume', True)
    gcd_chip.run()

    # Ensure import re-ran
    im_result = gcd_chip.find_result('v', step='import')
    assert im_result is not None
    assert os.path.getmtime(im_result) != old_im_result

    fp_result = gcd_chip.find_result('def', step='floorplan')
    assert fp_result is not None
    assert os.path.getmtime(fp_result) != old_fp_mtime

    # Ensure flow finished successfully
    assert gcd_chip.find_result('def', step='place') is None
