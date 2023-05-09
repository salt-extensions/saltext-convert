# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting to state file

.. versionadded:: 0.1

"""
import logging
import os
import pathlib
import re

import salt.daemons.masterapi  # pylint: disable=import-error
import salt.utils.files  # pylint: disable=import-error
import yaml
import pprint


__virtualname__ = "convert"

log = logging.getLogger(__name__)

MOD_BUILTINS = {
    "yum": "_process_pkg",
    "dnf": "_process_pkg",
    "ansible.builtin.yum": "_process_pkg",
    "service": "_process_service",
    "ansible.builtin.service": "_process_service",
    "seboolean": "_process_selinux"
}

LOOKUP_BUILTINS = {
    "with_items": "_process_with_items",
}

def __virtual__():
    return __virtualname__


def generate_files(state, sls_name="default", env="base"):
    """
    Generate an sls file for the minion with given state contents
    """
    minion_state_root = pathlib.Path("/srv/salt/ansible_convert")
    try:
        minion_state_root.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        log.warning(
            f"Unable to create directory {str(minion_state_root)}.  Check that the salt user has the correct permissions."
        )
        return False

    minion_state_file = minion_state_root / f"{sls_name}.sls"

    with salt.utils.files.fopen(minion_state_file, "w") as fp_:
        fp_.write(state)

    #generate_init(opts, minion, env=env)
    return minion_state_file


def _process_selinux(builtin_data, task):
    selinux_state = "selinux.boolean"

    for item in task:
        if item in LOOKUP_BUILTINS:
            lookup_data = task[item]
            globals()[LOOKUP_BUILTINS[item]](builtin_data, lookup_data)

    if "persistent" in builtin_data:
        state_contents = {selinux_state: [{"name": builtin_data["name"],
                                           "value": builtin_data["state"],
                                           "persist": builtin_data["persistent"]}]}
    else:
        state_contents = {selinux_state: [{"name": builtin_data["name"],
                                           "value": builtin_data["state"]}]}

    return state_contents



def _process_pkg(builtin_data, task):
    pkg_states = {"present": "pkg.installed",
                  "latest": "pkg.latest",
                  "absent": "pkg.removed"}

    for item in task:
        if item in LOOKUP_BUILTINS:
            lookup_data = task[item]
            globals()[LOOKUP_BUILTINS[item]](builtin_data, lookup_data)

    state_contents = {pkg_states[builtin_data["state"]]: [{"pkgs": builtin_data["name"]}]}
    return state_contents


def _process_service(builtin_data, task):
    service_states = {"started": "service.running",
                  "stopped": "service.dead"}

    for item in task:
        if item in LOOKUP_BUILTINS:
            lookup_data = task[item]
            ret = globals()[LOOKUP_BUILTINS[item]](builtin_data, lookup_data)

    if "enabled" in builtin_data:
        state_contents = {service_states[builtin_data["state"]]: [{"name": builtin_data["name"],
                                                                   "enable": builtin_data["enabled"]}]}
    else:
        state_contents = {service_states[builtin_data["state"]]: [{"name": builtin_data["name"]}]}
    return state_contents


def _process_with_items(builtin_data, lookup_data):
    value = "{{ item }}"
    key_list = [key for key, val in builtin_data.items() if val == value]
    for key in key_list:
        builtin_data[key] = lookup_data
    return builtin_data


def files(file=None, files=[]):
    if file:
        _files = [file]
    elif files:
        _files = files
    else:
        _files = []

    state_contents = {}
    for _file in _files:
        if not os.path.isfile(_file):
            log.error(f"File {_file} does not exist, skipping")
            continue
        with salt.utils.files.fopen(_file, "r") as fp_:
            json_data = yaml.safe_load(fp_.read())
            for block in json_data:
                if "tasks" in block:
                    tasks = block["tasks"]
                    for task in tasks:
                        task_name = task.pop("name")
                        for builtin in task:
                            builtin_func = globals().get(MOD_BUILTINS.get(builtin))
                            if builtin_func:
                                state_contents[task_name] = builtin_func(task[builtin], task)
                else:
                    task_name = block.pop("name")
                    for builtin in block:
                        builtin_func = globals().get(MOD_BUILTINS.get(builtin))
                        if builtin_func:
                            state_contents[task_name] = builtin_func(block[builtin], block)
            state_name = re.sub(".yml", "", f"{os.path.basename(_file)}")
            state_yaml =  yaml.dump(state_contents)
            generate_files(state=state_yaml, sls_name=state_name)
    return True
