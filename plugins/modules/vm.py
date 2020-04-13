#!/usr/bin/env python

#  Copyright 2019-2020 Gonéri Le Bouder
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

DOCUMENTATION = """
---
module: vm
short_description: A Cloud-like interface on top of a local Libvirt
author: "Gonéri Le Bouder"
requirements:
    - virt-lightning
options:
    distro:
        description:
            - name of the image to use
        required: true
"""

EXAMPLES = """
- name: Create a FreeBSD VM
  vm:
    distro: freebsd-12.0
    state: present
"""

RETURN = """
# Default return values
"""

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}


import virt_lightning.api
import virt_lightning.configuration


from ansible.module_utils.basic import AnsibleModule

try:
    import virt_lightning

    HAS_LIB = True
except ImportError:
    HAS_LIB = False


def get_vm(configuration, **vl_params):

    for i in virt_lightning.api.status(configuration, **vl_params):
        if i.get("name") == vl_params["name"]:
            return i


def main():
    argument_spec = dict(
        distro=dict(type=str),
        name=dict(type=str),
        state=dict(default="present"),
        groups=dict(default=[], type=list),
        root_disk_size=dict(type=int, default=32),
    )
    configuration = virt_lightning.configuration.Configuration()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)
    if not HAS_LIB:
        module.fail_json(
            msg="virt-lightning Python library is required for this module"
        )

    vl_params = module.params
    state = module.params.get("state", "present")
    del vl_params["state"]
    vm_found = get_vm(configuration, **vl_params)

    if state == "absent" and vm_found:
        virt_lightning.api.stop(configuration, **vl_params)
        module.exit_json(changed=True)
    elif state == "absent" and not vm_found:
        module.exit_json(changed=False)
    elif state == "present" and vm_found:
        module.exit_json(changed=False, **vm_found)
    elif state == "present" and not vm_found:
        virt_lightning.api.start(configuration, **vl_params)
        vm_found = get_vm(configuration, **vl_params)
        module.exit_json(changed=True, **vm_found)


if __name__ == "__main__":
    main()
