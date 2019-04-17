# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = '''
    name: virtlightning
    plugin_type: inventory
    version_added: '2.8'
    authors:
      - Gonéri Le Bouder
    short_description: Ansible dynamic inventory plugin for Virt Lightning.
    requirements:
        - python >= 3.6
    extends_documentation_fragment:
        - constructed
    description:
        - Expose the Virt-Lightning status as an inventory.
        - Uses a YAML configuration file virt_lightning.[yml|yaml].
'''

EXAMPLES = '''
# virtlightning.yml
plugin: virtlightning
'''

import libvirt

import virt_lightning.configuration
import virt_lightning.virt_lightning as vl

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils._text import to_native
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable


class InventoryModule(BaseInventoryPlugin, Constructable):
    ''' Host inventory parser for ansible using Gitlab API as source. '''

    NAME = 'virt_lightning'

    def verifyfile(self, path):
        """Return the possibly of a file being consumable by this plugin."""
        return (
            super(InventoryModule, self).verify_file(path) and
            path.endswith((self.NAME + ".yaml", self.NAME + ".yml")))

    def parse(self, inventory, loader, path, cache=False):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        try:
            configuration = virt_lightning.configuration.Configuration()
            conn = libvirt.open(configuration.libvirt_uri)
            hv = vl.LibvirtHypervisor(conn)
            groups = {}
            for domain in hv.list_domains():
                if domain.name not in self.inventory.hosts:
                    self.inventory.add_host(domain.name, group='all', port=22)
                    self.inventory.set_variable(domain.name, 'ansible_host', str(domain.ipv4.ip))
                    self.inventory.set_variable(domain.name, 'ansible_user', domain.username)
                    self.inventory.set_variable(domain.name, 'ansible_python_interpreter', '/usr/bin/python')
                    for group in domain.groups:
                        if group not in self.inventory.groups:
                            self.inventory.add_group(group)
                        self.inventory.groups[group].add_host(self.inventory.hosts[host_name])

        except Exception as e:
            raise AnsibleError('Something happened, this was original exception: %s' % to_native(e))
