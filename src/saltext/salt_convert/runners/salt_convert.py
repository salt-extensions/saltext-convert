# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting to state file

.. versionadded:: 0.0.1

"""
import importlib
import logging
import os
import pathlib
import re

import salt.daemons.masterapi  # pylint: disable=import-error
import salt.utils.files  # pylint: disable=import-error
import yaml


__virtualname__ = "convert"

log = logging.getLogger(__name__)


class PrettyDumper(yaml.SafeDumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()


def __virtual__():
    """
    Virtual function
    """
    return __virtualname__


def _setup_modules():
    """
    Load the utility modules
    """
    mod_builtins = {}
    utils_path = pathlib.Path(__file__).parent.parent / "utils" / "modules"
    for util_path in os.listdir(utils_path):
        fname, ext = os.path.splitext(util_path)
        if ext == ".py" and not fname.startswith("."):
            mod_name = f"saltext.salt_convert.utils.modules.{fname}"
            imported_mod = importlib.import_module(mod_name)
            if hasattr(imported_mod, "_setup"):
                mods = imported_mod._setup()
                for _mod in mods:
                    mod_builtins[_mod] = imported_mod.process
    return mod_builtins


def get_state_file_root(env="base"):
    """
    Get the state file root
    """
    return pathlib.Path(__opts__.get("file_roots").get(env)[0])


def generate_files(state, sls_name="default", file_type="sls", env="base"):
    """
    Generate an sls file for the minion with given state contents
    """
    minion_state_root = get_state_file_root(env=env) / "ansible_convert"

    try:
        minion_state_root.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        log.warning(
            f"Unable to create directory {str(minion_state_root)}.  "
            "Check that the salt user has the correct permissions."
        )
        return False

    minion_state_file = minion_state_root / f"{sls_name}.{file_type}"

    with salt.utils.files.fopen(minion_state_file, "w") as fp_:
        fp_.write(state)

    # generate_init(opts, minion, env=env)
    return minion_state_file


def files(path=None):
    mod_builtins = _setup_modules()

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
            playbook_path = pathlib.Path(_file).parent

            # Proccess vars
            for block in json_data:
                if "vars_files" in block:
                    vars_data = handle_vars(block["vars_files"], playbook_path)
                else:
                    vars_data = {}

            for block in json_data:
                if "tasks" in block:
                    tasks = block["tasks"]
                    for task in tasks:
                        task_name = task.pop("name")
                        for builtin in task:
                            builtin_func = mod_builtins.get(builtin)
                            if builtin_func:
                                state_contents[task_name] = builtin_func(
                                    task[builtin], task, vars_data
                                )
                else:
                    task_name = block.pop("name")
                    for builtin in block:
                        builtin_func = mod_builtins.get(builtin)
                        if builtin_func:
                            state_contents[task_name] = builtin_func(
                                block[builtin], block, vars_data
                            )

            state_name = re.sub(".yml", "", f"{os.path.basename(_file)}")
            state_yaml = yaml.dump(state_contents, Dumper=PrettyDumper, sort_keys=False)
            breakpoint()

            include_yaml = ""
            for include in vars_data:
                include_yaml = (
                    include_yaml
                    + '{% import_yaml tpldir ~ "/'
                    + include
                    + '.yml" as '
                    + include
                    + " with context -%}\n\n"
                )
            state_yaml = include_yaml + state_yaml

            sls_files.append(generate_files(state=state_yaml, sls_name=state_name))
    return {"Converted playbooks to sls files": [str(x) for x in sls_files]}


def handle_vars(path=None, parent_path=None):
    include_vars = {}
    _files = []

    if not isinstance(path, list):
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

    for _file in _files:
        if not str(_file).startswith(os.sep):
            var_file = parent_path / _file
        else:
            var_file = _file

        var_include_name = re.sub(".yml", "", f"{os.path.basename(_file)}")

        with salt.utils.files.fopen(var_file, "r") as fp_:
            yaml_data = yaml.safe_load(fp_.read())
            vars_yaml = yaml.dump(yaml_data)

            vars_include_file = generate_files(
                state=vars_yaml, sls_name=var_include_name, file_type="yml"
            )

            include_vars[var_include_name] = {"data": yaml_data, "file": str(vars_include_file)}

    return include_vars
