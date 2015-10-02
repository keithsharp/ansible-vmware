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

COMMENT_CHAR = '#'
OPTION_CHAR = '='
SUBKEY_CHAR = '.'

class VMXParser(object):

	options = {}

	def __init__(self, vmxfile):
		f = open(vmxfile)
		for line in f:
			if COMMENT_CHAR in line:
				line, comment = line.split(COMMENT_CHAR, 1)
				if not line:
					continue
			if OPTION_CHAR in line:
				key, value = line.split(OPTION_CHAR, 1)
				if key == ".encoding":
					continue
				key = key.strip()
				value = value.strip()
				value = value[1:-1]
				self.options[key] = value
		f.close()
