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
    - virt-lightning
  tasks:
    - name: Create the Debian 9 VM
      virtlightning:
        distro: debian-9
        name: vm1
        state: present

    - name: Refresh inventory to ensure new instaces exist in inventory
      meta: refresh_inventory

    - name:
      command: uname -a
      delegate_to: vm1

    - name: Destroy the VM
      virtlightning:
        name: vm1
        state: absent
```

## Installation

```shell
mkdir -p ~/.ansible/collections/ansible_collections
git clone http://github.com/virt-lightning/ansible-collection-virt-lightning.git ~/.ansible/collections/ansible_collections/virtlightning
```
