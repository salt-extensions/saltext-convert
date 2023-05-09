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
import saltext.salt_convert.utils.pkg
import saltext.salt_convert.utils.selinux
import saltext.salt_convert.utils.service


__virtualname__ = "convert"

log = logging.getLogger(__name__)

MOD_BUILTINS = {
    "yum": saltext.salt_convert.utils.pkg.process_pkg,
    "dnf": saltext.salt_convert.utils.pkg.process_pkg,
    "ansible.builtin.yum": saltext.salt_convert.utils.pkg.process_pkg,
    "service": saltext.salt_convert.utils.service.process_service,
    "ansible.builtin.service": saltext.salt_convert.utils.service.process_service,
    "seboolean": saltext.salt_convert.utils.selinux.process_selinux,
    "ansible.posix.seboolean": saltext.salt_convert.utils.selinux.process_selinux,

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


def files(path=None):
    _files = []
    if not isinstance(path, dict):
        _files = [path]
    else:
        _files = path

    _files = [pathlib.Path(x) for x in _files]
    # check if directory and add each file to _files dict
    for _file in _files:
        if _file.is_dir():
            for _path in _file.iterdir():
                _files.append(_path)
                if _file in _files:
                    _files.remove(_file)

    state_contents = {}
    sls_files = []
    for _file in _files:
        if not _file.is_file():
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
                            builtin_func = MOD_BUILTINS.get(builtin)
                            if builtin_func:
                                state_contents[task_name] = builtin_func(task[builtin], task)
                else:
                    task_name = block.pop("name")
                    for builtin in block:
                        builtin_func = MOD_BUILTINS.get(builtin)
                        if builtin_func:
                            state_contents[task_name] = builtin_func(block[builtin], block)
            state_name = re.sub(".yml", "", f"{os.path.basename(_file)}")
            state_yaml =  yaml.dump(state_contents)
            sls_files.append(generate_files(state=state_yaml,
                                            sls_name=state_name))
    return {"Converted playbooks to sls files": [str(x) for x in sls_files]}
