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

## Virtual Machine Status
This module allows you to start and stop virtual machines.  You can test this with the
example playbooks provided.  To start all virtual machines on your system that are
currently in state stopped

    ansible-playbook -i ./inventory/vm_inventory.py -M ./module ./playbooks/start-vm.yml

And to stop all virtual machines that are currently running on your system:

    ansible-playbook -i ./inventory/vm_inventory.py -M ./module ./playbooks/stop-vm.yml

Within the playbook the key task is:

    vm_status: vmxfile="{{ vmxfile }}" state=running headless=yes

There are three variables you can pass to the task:

* **vmxfile** which is the path to the VMX file describing the virtual machine.  Note
that you need the quotes in case the path as spaces within it.
* **state** can be either running or stopped and indicates the desired state you want
to put the virtual machine into.
* **headless** can be either yes or no, and defaults to yes.  This determines wether a 
GUI console is created for the virtual machine and is only relevant when state=running.

Note that the module uses the vmrun command, however due to an issue with global
variables in Ansible modules I had to spread references to the command in three different
functions.  If your VMWare Fusion install is in a non-standard location you will need to
change the vmrun command in these three locations.
