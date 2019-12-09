#!/bin/bash
test -d venv || virtualenv -p python3 venv
source venv/bin/activate
pip install virt-lightning ansible
ansible-playbook playbook.yml -vvvv -i inventory.yaml
