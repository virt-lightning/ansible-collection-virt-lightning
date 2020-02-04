# Virt-Lightning's Ansible collection

## Purpose

This module extends Ansible feature to provide two additional plugins. These
plugins allow you to consume the `virt-lightning` inventory and manage new
virtual machine:

## Example

```yaml
---
- hosts: localhost
  collections:
    - virt_lightning.virt_lightning
  tasks:
    - name: Create the Debian 10 VM
      virt_lightning:
        distro: debian-10
        name: myvm
        state: present

    - name: Refresh inventory to ensure new instaces exist in inventory
      meta: refresh_inventory

    - debug: var=hostvars.myvm
    - name:
      command: uname -a
      delegate_to: myvm

    - name: Destroy the VM
      virt_lightning:
        name: myvm
        state: absent
```

## Requirements

- Libvirt
- Linux

VirtLightning should already be installed in your virtualenv, the following command
should not raise any error: `python -m virt_lightning.virt_lightning`

If it's not the case, just follow the installation procedure here: https://virt-lightning.github.io/virt-lightning/

## Installation

```shell
ansible-galaxy collection install -p ~/.ansible/collections virt_lightning.virt_lightning
```

You can test your installation with the two samples playbooks.
