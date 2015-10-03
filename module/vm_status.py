#! /usr/bin/env python

# Copyright 2015, Keith Sharp <keith.sharp@gmail.com>

# This file is part of Ansible-VMware.
#
# Ansible-VMware is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible-VMware is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible-VMware.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = """
module: vm_status
version_added: "0.1"
short_description: start and stop pre-existing virtual machines
description:
  - Start and stop virtual machines based on VMX files from dynamic inventory.
  - Optionally start the virtual machine with or without a GUI (headless mode).
options:
  vmxfile:
    required: true
    description:
      - Path to the VMX file that defines the virtual machine
  state:
    required: true
    description:
      - The desired state of the virtual machine
    choices: [ "running", "stopped" ]
  headless:
    required: false
    choices: [ "yes", "no" ]
    default: "yes"
    description:
      - If true, start the virtual machine without a GUI
requires: [ passlib>=1.6 ]
author: "Keith Sharp <keith.sharp@gmail.com>"
"""

EXAMPLES = """
# Start a virtual machine without a GUI
- vm_status: vmxfile=/path/to/my/machine.vmx state=running
# Start a virtual machine with a GUI
- vm_status: vmxfile=/path/to/my/machine.vmx state=running headless=no
# Stop a virtual machine
- vm_status: vmxfile=/path/to/my/machine.vmx state=stopped
"""

import os
import subprocess

def get_vm_state(vmxfile):
    output = subprocess.check_output(["/Applications/VMware Fusion.app/Contents/Library/vmrun",
                                      "-T", "fusion", "list"])
    for line in output.splitlines():
        if "Total running VMs:" in line:
            continue
        elif vmxfile == line:
            return "running"
    return "stopped"

def get_vm_name(vmxfile):
    COMMENT_CHAR = '#'
    OPTION_CHAR = '='
    name = None
    f = open(vmxfile, "r")
    for line in f:
        if COMMENT_CHAR in line:
            line, comment = line.split(COMMENT_CHAR, 1)
            if not line:
                continue
        if OPTION_CHAR in line:
            key, value = line.split(OPTION_CHAR, 1)

            key = key.strip()
            if key == "name":
                name = value.strip()
                name = name[1:-1]
                break
    f.close()
    if not name:
        name = os.path.basename(vmxfile)
    return name

def start_virtual_machine(vmxfile, headless, check_mode):
    state = get_vm_state(vmxfile)
    name = get_vm_name(vmxfile)
    command = ["/Applications/VMware Fusion.app/Contents/Library/vmrun", "-T", "fusion",
               "start", os.path.normpath(vmxfile)]

    if headless == "yes":
        command.append("nogui")
    elif headless == "no":
        command.append("gui")
    else:
        raise ValueError("%s is not a valid option for headless" % headless)

    if state == "stopped":
        if check_mode:
            changed = False
        else:
            output = subprocess.check_output(command)
            changed = True
        msg="Started virtual machine: %s" % name
    elif state == "running":
        changed = False
        msg="Virtual machine: %s is already running" % name
    else:
        raise ValueError("%s is not a valid option for state" % state)

    return (msg, changed)

def stop_virtual_machine(vmxfile, check_mode):
    state = get_vm_state(vmxfile)
    name = get_vm_name(vmxfile)
    command = ["/Applications/VMware Fusion.app/Contents/Library/vmrun", "-T", "fusion",
               "stop", os.path.normpath(vmxfile)]

    if state == "running":
        if check_mode:
            changed = False
        else:
            output = subprocess.check_output(command)
            changed = True
        msg="Stopped virtual machine: %s" % name
    elif state == "stopped":
        changed = False
        msg="Virtual machine: %s is already stopped" % name
    else:
        raise ValueError("%s is not a valid option for state" % state)

    return (msg, changed)

def main():
    arg_spec = dict(state = dict(required = True),
                    vmxfile = dict(required = True),
                    headless = dict(default = "yes"))
    module = AnsibleModule(argument_spec = arg_spec, supports_check_mode = True)

    vmxfile = module.params['vmxfile']
    state = module.params['state']
    headless = module.params['headless']
    check_mode = module.check_mode

    try:
        if state == 'running':
            (msg, changed) = start_virtual_machine(vmxfile, headless, check_mode)
        elif state == 'stopped':
            (msg, changed) = stop_virtual_machine(vmxfile, check_mode)
        else:
            module.fail_json(msg="Invalid state: %s" % state)

        module.exit_json(msg=msg, changed=changed)
    except Exception, e:
        module.fail_json(msg=str(e))

from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
