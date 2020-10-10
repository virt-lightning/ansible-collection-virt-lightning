#!/usr/bin/env python

#  Copyright 2019 Gonéri Le Bouder
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

DOCUMENTATION = '''
---
module: virt_lightning
short_description: A Cloud-like interface on top of a local Libvirt
description:
    - Foo
    - Bar
author: "Gonéri Le Bouder"
version_added: "2.9"
requirements:
    - virt-lightning
options:
    distro:
        description:
            - name of the image to use
        required: true
'''

EXAMPLES = '''
# single check on 192.168.1.1 with credentials admin/admin
- name: ensure the FreeBSD VM is running
  virt_lightning:
    distro: freebsd-12.0
    state: present
'''

RETURN = '''
# Default return values
'''

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

import re
import asyncio

import libvirt
import virt_lightning.configuration
import virt_lightning.virt_lightning as vl


from ansible.module_utils.basic import AnsibleModule
try:
    import virt_lightning
    HAS_LIB = True
except ImportError:
    HAS_LIB = False

def create(hv, configuration, distro, context, name, root_disk_size, **kwargs):
    user_config = {
        "groups": kwargs.get("groups"),
        "memory": kwargs.get("memory"),
        "python_interpreter": kwargs.get("python_interpreter"),
        "root_password": kwargs.get("root_password", configuration.root_password),
        "ssh_key_file": kwargs.get("ssh_key_file", configuration.ssh_key_file),
        "username": kwargs.get("username"),
        "vcpus": kwargs.get("vcpus"),
        "fqdn": kwargs.get("fqdn"),
        "default_nic_mode": kwargs.get("default_nic_model"),
    }
    domain = hv.create_domain(name=name, distro=distro)
    hv.configure_domain(domain, user_config)
    domain.context = context
    root_disk_path = hv.create_disk(
        name=name,
        backing_on=distro,
        size=root_disk_size,
    )
    domain.add_root_disk(root_disk_path)
    network = {
        "network": configuration.network_name,
        "ipv4": hv.get_free_ipv4(),
        }
    # Virt-Lightning 2.0.0
    if hasattr(domain, "attach_network"):
        domain.attach_network(**network)
    else:
        domain.attachNetwork(**network)
    hv.start(domain, metadata_format={"provider": "opensack"})
    loop = asyncio.get_event_loop()

    async def deploy():
        await domain.reachable()
    loop.run_until_complete(deploy())
    return domain

def main():
    argument_spec = dict(
        distro=dict(type=str),
        name=dict(type=str),
        state=dict(default='present'),
        context=dict(type=str, default='default'),
        root_password=dict(type=str),
        groups=dict(default=[], type=list),
        memory=dict(type=int, default=512),
        vcpus=dict(type=int, default=1),
        root_disk_size=dict(type=int, default=32)
    )
    configuration = virt_lightning.configuration.Configuration()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)
    if not HAS_LIB:
        module.fail_json(msg='virt-lightning Python library is required for this module')

    state = module.params['state']
    context = module.params['context']
    distro = module.params['distro']
    groups = module.params['groups']
    root_password = module.params['root_password'] or configuration.root_password
    name = module.params.get('name') or re.sub(r"\W+", "", distro)
    memory = module.params['memory']
    vcpus = module.params['vcpus']
    root_disk_size = module.params['root_disk_size']


    conn = libvirt.open(configuration.libvirt_uri)
    hv = vl.LibvirtHypervisor(conn)
    hv.init_network(configuration.network_name, configuration.network_cidr)
    hv.init_storage_pool(configuration.storage_pool)
    domain = hv.get_domain_by_name(name)

    if state == 'absent' and domain:
        hv.clean_up(domain)
        module.exit_json(changed=True)
    elif state == 'absent' and not domain:
        module.exit_json(changed=False)
    elif state == 'present' and domain:
        module.exit_json(changed=False)
    else:
        domain = create(hv, configuration, distro, context, name,
                        root_disk_size, memory=memory, vcpus=vcpus,
                        groups=groups)
        module.exit_json(
            changed=True,
            name=domain.name,
            ipv4=str(domain.ipv4.ip))


if __name__ == '__main__':
    main()
