# Ansible module for VMware Fusion
Copyright 2015, Keith Sharp <keith.sharp@gmail.com>, licensed under the GPLv3

This Ansible module provides the ability to create and manage VMware Fusion
virtual machines.

## Dynamic Inventory
This module contains a dynamic inventory provider that pulls information about the 
virtual machines on your system from two sources:

1. There is a filesystem search path hardcoded into the top of the file
inventory/vm_inventory.py.  We search for VMX files under this directory and then
parse them to extract information about the virtual machines.

2. We use the vmrun command (path is hardcoded at the top of the inventory/vm_inventory.py
file) to list all the running virtual machines on the system and their corresponding
VMX files.   We parse these VMX files for information about the virtual machines.

Three groups of machines are created:

* **allvms**  which contains all virtual machines on the system no matter what their
state.
* **stopped** which contains all virtual machines that are not running.
* **running** which contains all virtual machines that are running.

In addition each virtual machine has two variables associated with it:

* **state** whether the virtual machine is running or stopped.
* **vmxfile** the full path to the VMX file that defines the virtual machine.

To test the inventor is working first edit the vmrun and vmdirs variables at the top of
the inventory/vm_inventory.py file to match you setup, then run the command:

    ./inventory/vm_inventory.py

This should provide JSON output matching the virtual machines you have configured.  You 
can examine an individual virtual machine with the command:

    ./inventory/vm_inventory.py --host <machine name>