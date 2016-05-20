#!/usr/bin/env python
"""Test netmiko_grep utility."""
from __future__ import print_function
from __future__ import unicode_literals

import time
import subprocess
import re
import os
import shutil
import uuid

from netmiko.utilities import obtain_netmiko_filename, write_tmp_file, ensure_dir_exists
from netmiko.utilities import find_netmiko_dir

NETMIKO_GREP = '/home/gituser/netmiko_tools/netmiko_tools/netmiko-grep'

def convert_bytes_to_str(my_bytes):
    try:
        return my_bytes.decode("utf-8")
    except AttributeError:
        return my_bytes


def subprocess_handler(cmd_list):
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    results = proc.communicate()
    (output, std_err) = [convert_bytes_to_str(x) for x in results]
    return (output, std_err)


def test_version():
    cmd_list = [NETMIKO_GREP] + ['--version']
    (output, std_err) = subprocess_handler(cmd_list)
    assert 'netmiko-grep v0.' in output.strip()
    assert std_err == ''


def test_list_devices():
    cmd_list = [NETMIKO_GREP] + ['--list-devices']
    output_patterns = ['Devices', 'Groups', 'pynet_rtr1', 'all', 'cisco']
    (output, std_err) = subprocess_handler(cmd_list)
    for pattern in output_patterns:
        assert pattern in output
    assert std_err == ''


def test_missing_args():
    cmd_list = [NETMIKO_GREP] + []
    output_patterns = ['']
    stderr_patterns = ['error: Grep pattern or devices not specified.']
    (output, std_err) = subprocess_handler(cmd_list)
    assert output == ''
    for pattern in output_patterns:
        assert pattern in output
    for pattern in stderr_patterns:
        assert pattern in std_err


def test_single_device():
    cmd_list = [NETMIKO_GREP] + ['interface', 'pynet_rtr1']
    output_patterns = [
        'interface FastEthernet0',
        'interface FastEthernet1',
        'interface FastEthernet2',
        'interface FastEthernet3',
        'interface FastEthernet4',
        'interface Vlan1',
    ]
    (output, std_err) = subprocess_handler(cmd_list)
    for pattern in output_patterns:
        assert pattern in output
    assert std_err == ''


def test_group():
    cmd_list = [NETMIKO_GREP] + ['interface', 'cisco']
    output_patterns = [
        'pynet_rtr2.txt:interface FastEthernet0',
        'pynet_rtr2.txt:interface FastEthernet1',
        'pynet_rtr2.txt:interface FastEthernet2',
        'pynet_rtr2.txt:interface FastEthernet3',
        'pynet_rtr2.txt:interface FastEthernet4',
        'pynet_rtr2.txt:interface Vlan1',
        'pynet_rtr1.txt:interface FastEthernet0',
        'pynet_rtr1.txt:interface FastEthernet1',
        'pynet_rtr1.txt:interface FastEthernet2',
        'pynet_rtr1.txt:interface FastEthernet3',
        'pynet_rtr1.txt:interface FastEthernet4',
        'pynet_rtr1.txt:interface Vlan1',
    ]
    (output, std_err) = subprocess_handler(cmd_list)
    for pattern in output_patterns:
        assert pattern in output
    assert std_err == ''


def test_group_all():
    cmd_list = [NETMIKO_GREP] + ['interface', 'all']
    output_patterns = [
        'pynet_rtr2.txt:interface FastEthernet0',
        'pynet_rtr2.txt:interface FastEthernet1',
        'pynet_rtr2.txt:interface FastEthernet2',
        'pynet_rtr2.txt:interface FastEthernet3',
        'pynet_rtr2.txt:interface FastEthernet4',
        'pynet_rtr2.txt:interface Vlan1',
        'pynet_rtr1.txt:interface FastEthernet0',
        'pynet_rtr1.txt:interface FastEthernet1',
        'pynet_rtr1.txt:interface FastEthernet2',
        'pynet_rtr1.txt:interface FastEthernet3',
        'pynet_rtr1.txt:interface FastEthernet4',
        'pynet_rtr1.txt:interface Vlan1',
        'cisco_asa.txt:interface Ethernet0/0',
        'cisco_asa.txt:interface Vlan1',
        'cisco_xrv.txt:interface MgmtEth0/0/CPU0/0',
        'cisco_xrv.txt:interface GigabitEthernet0/0/0/0',
        'juniper_srx.txt:                interface vlan.0;',
        'juniper_srx.txt:        l3-interface vlan.0;',
        'arista_sw1.txt:interface Ethernet1',
        'arista_sw2.txt:interface Ethernet1',
        'arista_sw2.txt:interface Ethernet2',
        'arista_sw2.txt:interface Ethernet3',
        'arista_sw2.txt:interface Ethernet4',
        'arista_sw2.txt:interface Ethernet5',
        'arista_sw2.txt:interface Ethernet6',
        'arista_sw2.txt:interface Ethernet7',
        'arista_sw2.txt:interface Management1',
        'arista_sw2.txt:interface Vlan1',
        'arista_sw3.txt:interface Ethernet1',
        'arista_sw4.txt:interface Ethernet1',
    ]
    (output, std_err) = subprocess_handler(cmd_list)
    for pattern in output_patterns:
        assert pattern in output
    assert std_err == ''


def test_cmd_single_device():
    cmd_list = [NETMIKO_GREP] + ['--cmd', 'show arp', '10.220.88.', 'pynet_rtr1']
    output_patterns = [
        'Internet  10.220.88.20            -   c89c.1dea.0eb6  ARPA',
    ]
    (output, std_err) = subprocess_handler(cmd_list)
    for pattern in output_patterns:
        assert pattern in output
    assert std_err == ''


def test_cmd_group():
    cmd_list = [NETMIKO_GREP] + ['--cmd', 'show arp', '10.220.88.', 'cisco']
    output_patterns = [
        'pynet_rtr1.txt:Internet  10.220.88.20            -   c89c.1dea.0eb6  ARPA',
        'pynet_rtr2.txt:Internet  10.220.88.21            -   1c6a.7aaf.576c  ARPA',
    ]
    (output, std_err) = subprocess_handler(cmd_list)
    for pattern in output_patterns:
        assert pattern in output
    assert std_err == ''


def test_use_cache():
    """With cached files this should come back in under a second"""
    # Generate cached files
    cmd_list = [NETMIKO_GREP] + ['interface', 'all']
    subprocess_handler(cmd_list)
    cmd_list = [NETMIKO_GREP] + ['--use-cache', '--display-runtime', 'interface', 'all']
    (output, std_err) = subprocess_handler(cmd_list)
    match = re.search(r"Total time: (0:.*)", output)
    time = match.group(1)
    _, _, seconds = time.split(":")
    seconds = float(seconds)
    assert seconds <= 1
    assert 'pynet_rtr1.txt:interface FastEthernet0' in output


def test_use_cache_missing_file():
    """Test use_cache with a missing cache file. Should generate error."""
    # Generate cached files
    cmd_list = [NETMIKO_GREP] + ['interface', 'all']
    _, full_dir = find_netmiko_dir()
    remove_file = 'bad_device.txt'
    remove_file_full = "{}/{}".format(full_dir, remove_file)
    if os.path.exists(remove_file_full) and os.path.isfile(remove_file_full):
        os.remove(remove_file_full)
    cmd_list = [NETMIKO_GREP] + ['--use-cache', '--display-runtime', 'interface', 'all']
    (output, std_err) = subprocess_handler(cmd_list)
    assert "Some cache files are missing: unable to use --use-cache option." in std_err


def test_display_failed():
    """Verify failed devices are showing"""
    cmd_list = [NETMIKO_GREP] + ['interface', 'all']
    (output, std_err) = subprocess_handler(cmd_list)
    assert "Failed devices" in output
    failed_devices = output.split("Failed devices:")[1]
    failed_devices = failed_devices.strip().split("\n")
    failed_devices = [x.strip() for x in failed_devices]
    assert len(failed_devices) == 2
    assert "bad_device" in failed_devices
    assert "bad_port" in failed_devices


def test_hide_failed():
    """Verify failed devices are showing"""
    cmd_list = [NETMIKO_GREP] + ['--hide-failed', 'interface', 'all']
    (output, std_err) = subprocess_handler(cmd_list)
    assert "Failed devices" not in output


def test_find_netmiko_dir():
    """Test function that finds netmiko_dir."""
    base_dir_check = '/home/gituser/.netmiko'
    full_dir_check = '/home/gituser/.netmiko/tmp'
    base_dir, full_dir = find_netmiko_dir()
    assert base_dir == base_dir_check and full_dir == full_dir_check


def test_obtain_netmiko_filename():
    """Test file name and that directory is created."""
    create_dir_test = True
    file_name_test = '/home/gituser/.netmiko/tmp/test_device.txt'
    file_name = obtain_netmiko_filename('test_device')
    assert file_name == file_name_test

    if create_dir_test:
        uuid_str = str(uuid.uuid1())
        junk_dir_base = '/home/gituser/JUNK/netmiko'
        junk_dir = '{}/{}'.format(junk_dir_base, uuid_str)
        base_dir, full_dir = find_netmiko_dir()
        print(base_dir)

        # Move base_dir and recreate it
        if os.path.isdir(base_dir) and os.path.isdir(junk_dir_base):
            shutil.move(src=base_dir, dst=junk_dir)
        assert os.path.exists(base_dir) == False
        assert os.path.exists(full_dir) == False
        file_name = obtain_netmiko_filename('test_device')
        ensure_dir_exists(base_dir)
        ensure_dir_exists(full_dir)
        assert os.path.exists(base_dir) == True
        assert os.path.exists(full_dir) == True

