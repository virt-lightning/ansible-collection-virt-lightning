#!/bin/bash
test -d venv || virtualenv -p python3 venv
source venv/bin/activate
test -f venv/bin/ansible || pip install virt-lightning ansible
ansible-playbook playbook.yml -vvvv -i inventory.yaml
