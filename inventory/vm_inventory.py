#!/usr/bin/env python

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

import fnmatch
import subprocess
import os
import sys
import VMXParser
import json
import argparse

# Change these depending on where vmrun lives and whether you are running
# Fusion on Workstation
vmrun = "/Applications/VMware Fusion.app/Contents/Library/vmrun"
type = "fusion"

# Change this to create a list of directories where you save VMs
vmdirs = ["/Users/kms/Documents/Virtual Machines.localized"]

def get_running_vms():
    vms = []
    output = subprocess.check_output([vmrun, "-T", type, "list"])
    for line in output.splitlines():
        if "Total running VMs:" in line:
            continue
        vm = get_vmdetails_from_vmx_file(line)
        vm["state"] = "running"
        vms.append(vm)
    return vms

def get_vmx_files_in_dirs(dirs):
    vmxfiles = []
    for dir in dirs:
        for root, subdirs, files in os.walk(dir):
            for filename in files:
                fullpath = os.path.join(root, filename)
                if fnmatch.filter([fullpath], "*.vmx"):
                    vmxfiles.append(fullpath)
    return vmxfiles

def get_vmdetails_from_vmx_file(vmxfile):
    vm = {}
    parser = VMXParser.VMXParser(vmxfile)
    config = parser.options
    if "displayName" in config:
        vm["name"] = config["displayName"]
    else:
        vm["name"] = os.path.basename(file)
    vm["vmxfile"] = vmxfile
    vm['state'] = "stopped"
    config.clear()
    return vm

def print_full_inventory(vms):
    inventory = {}
    vmhosts = []
    running = []
    stopped = []
    hostvars = {}
    for vm in vms:
        vmhosts.append(vm["name"])
        if vm["state"] == "running":
            running.append(vm["name"])
        else:
            stopped.append(vm["name"])
        vmxdict = { "vmxfile" : vm["vmxfile"] }
        hostvars[vm["name"]] = vmxdict
        
    inventory["allvms"] = { "hosts" : vmhosts }
    inventory["running"] = { "hosts" : running }
    inventory["stopped"] = { "hosts" : stopped }
    inventory["_meta"] = { "hostvars" : hostvars }

    print(json.dumps(inventory))

def print_host_inventory(vms, host):
    for vm in vms:
        if vm["name"] == host:
            hostvars = {"vmxfile" : vm["vmxfile"], "state" : vm["state"]}
            print(json.dumps(hostvars))

parser = argparse.ArgumentParser(description='Produce an Ansible Inventory file based on VMs')
group = parser.add_mutually_exclusive_group()
group.add_argument('--list', action='store_true', help='List servers')
group.add_argument('--host', action='store', help='Get the variables about a specific server')
args = parser.parse_args()

vms = []
vmxfiles = get_vmx_files_in_dirs(vmdirs)
for file in vmxfiles:
    vms.append(get_vmdetails_from_vmx_file(file))

rvms = get_running_vms()

for rvm in rvms:
    for vm in vms:
        if vm["vmxfile"] == rvm["vmxfile"]:
            vm["state"] = rvm["state"]

if args.host is not None:
    print_host_inventory(vms, args.host)
else:
    print_full_inventory(vms)
    
