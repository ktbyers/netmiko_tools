#!/usr/bin/env python
"""Test netmiko_grep utility."""
from __future__ import print_function
from __future__ import unicode_literals

import time
import subprocess

NETMIKO_GREP = '/home/gituser/netmiko_tools/netmiko_tools/netmiko-grep'

def test_list_devices():
    cmd_list = [NETMIKO_GREP] + ['--list-devices']
    output_patterns = ['Devices', 'Groups', 'pynet_rtr1', 'all', 'cisco']
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, std_err) = proc.communicate()
    for pattern in output_patterns:
        assert pattern in output


def test_missing_args():
    cmd_list = [NETMIKO_GREP] + []
    output_patterns = ['']
    stderr_patterns = ['error: Grep pattern or devices not specified.']
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, std_err) = proc.communicate()
    assert output == ''
    for pattern in output_patterns:
        assert pattern in output
    for pattern in stderr_patterns:
        assert pattern in std_err
