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


def _setup_modules(module_type=None):
    """
    Load the utility modules
    """
    mod_builtins = {}
    if not module_type:
        log.error("Need a module type")
        return mod_builtins

    utils_path = pathlib.Path(__file__).parent.parent / "utils" / module_type / "modules"
    for util_type in os.listdir(utils_path):
        utils_path = (
            pathlib.Path(__file__).parent.parent / "utils" / module_type / "modules" / util_type
        )
        for util_path in os.listdir(utils_path):
            fname, ext = os.path.splitext(util_path)
            if ext == ".py" and not fname.startswith("."):
                mod_name = f"saltext.salt_convert.utils.{module_type}.modules.{util_type}.{fname}"
                imported_mod = importlib.import_module(mod_name)
                if hasattr(imported_mod, "_setup"):
                    mods = imported_mod._setup()
                    if mods:
                        for _mod in mods:
                            mod_builtins[_mod] = imported_mod.process
    return mod_builtins


def get_state_file_root(env="base"):
    """
    Get the state file root
    """
    return pathlib.Path(__opts__.get("file_roots").get(env)[0])


def generate_files(state, sls_name="default", file_type="sls", env="base", convert_dir="converted"):
    """
    Generate an sls file for the minion with given state contents
    """
    minion_state_root = get_state_file_root(env=env) / convert_dir

    try:
        minion_state_root.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        log_mesg = (
            f"Unable to create directory {str(minion_state_root)}.  "
            "Check that the salt user has the correct permissions."
        )
        log.warning(log_mesg)
        return False

    minion_state_file = minion_state_root / f"{sls_name}.{file_type}"

    with salt.utils.files.fopen(minion_state_file, "w") as fp_:
        fp_.write(state)

    # generate_init(opts, minion, env=env)
    return minion_state_file


def ansible_files(path=None):
    mod_builtins = _setup_modules(module_type="ansible")

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
    notify_tasks = {}
    for _file in _files:
        if not _file.is_file():
            log.error("File %s does not exist, skipping", _file)
            continue
        with salt.utils.files.fopen(_file, "r") as fp_:
            json_data = yaml.safe_load(fp_.read())
            playbook_path = pathlib.Path(_file).parent

            # Proccess vars
            for block in json_data:
                if "vars_files" in block:
                    vars_data = handle_ansible_vars(block["vars_files"], playbook_path)
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
                        if "notify" in task:
                            if task["notify"] not in notify_tasks:
                                notify_tasks[task["notify"]] = [
                                    task_name,
                                ]
                            else:
                                notify_tasks[task["notify"]].append(task_name)
                else:
                    task_name = block.pop("name", None)
                    for builtin in block:
                        builtin_func = mod_builtins.get(builtin)
                        if builtin_func:
                            if not task_name:
                                task_name = block[builtin]
                            data = builtin_func(block[builtin], block, vars_data)
                            if isinstance(data, list):
                                count = 0
                                for state in data:
                                    state_name = task_name + str(count)
                                    state_contents[state_name] = state
                                    count += 1
                            else:
                                state_contents[task_name] = data

            for block in json_data:
                if "handlers" in block:
                    handlers = block["handlers"]
                    handler_states = {}
                    for handler in handlers:
                        handler_name = handler.pop("name")
                        has_listen = handler.pop("listen", False)
                        for builtin in handler:
                            builtin_func = mod_builtins.get(builtin)
                            if builtin_func:
                                state_contents[handler_name] = builtin_func(
                                    handler[builtin], handler, vars_data
                                )
                                if has_listen:
                                    handler_state_name = has_listen
                                else:
                                    handler_state_name = handler_name

                                if handler_state_name not in handler_states:
                                    handler_states[handler_state_name] = [
                                        state_contents[handler_name]
                                    ]
                                else:
                                    handler_states[handler_state_name].append(
                                        state_contents[handler_name]
                                    )

                    for notify_task, val in notify_tasks.items():
                        if notify_task in handler_states:
                            for state_name in notify_tasks[notify_task]:
                                if state_name in state_contents:
                                    for req in handler_states[notify_task]:
                                        state_func = next(iter(state_contents[state_name]))

                                        notify_func = next(iter(req))
                                        notify_mod = notify_func.split(".")[0]
                                        notify_name = req[notify_func][0]["name"]

                                        if not [
                                            True
                                            for state in state_contents[state_name][state_func]
                                            if "listen_in" in state
                                        ]:
                                            state_contents[state_name][state_func].append(
                                                {"listen_in": [{notify_mod: notify_name}]}
                                            )
                                        else:
                                            for _state in state_contents[state_name][state_func]:
                                                if "listen_in" in _state:
                                                    _state["listen_in"].append(
                                                        {notify_mod: notify_name}
                                                    )

            state_name = re.sub(".yml", "", f"{os.path.basename(_file)}")
            state_yaml = yaml.dump(state_contents, Dumper=PrettyDumper, sort_keys=False)

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

            sls_files.append(
                generate_files(state=state_yaml, sls_name=state_name, convert_dir="ansible_convert")
            )
    return {"Converted playbooks to sls files": [str(x) for x in sls_files]}


def handle_ansible_vars(path=None, parent_path=None):
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
                state=vars_yaml,
                sls_name=var_include_name,
                file_type="yml",
                convert_dir="ansible_convert",
            )

            include_vars[var_include_name] = {"data": yaml_data, "file": str(vars_include_file)}

    return include_vars


def chef_files(path=None):
    mod_builtins = _setup_modules(module_type="chef")

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
    notify_tasks = {}
    for _file in _files:
        if not _file.is_file():
            log.error("File %s does not exist, skipping", _file)
            continue
        with salt.utils.files.fopen(_file, "r") as fp_:
            json_data = _chef_parse(fp_.read())

            for block in json_data:
                builtin_func = mod_builtins.get(block["type"])
                if builtin_func:
                    data = builtin_func(block)
                    state_name = f"{block['type']}_{block['name']}"
                    state_contents[state_name] = data

            state_yaml = yaml.dump(state_contents, Dumper=PrettyDumper, sort_keys=False)

            sls_files.append(
                generate_files(state=state_yaml, sls_name=state_name, convert_dir="chef_convert")
            )

    return {"Converted chef recipes to sls files": [str(x) for x in sls_files]}


def _chef_parse(contents):
    # Regex patterns to identify Chef resources
    resource_pattern = re.compile(r"(\w+)\s'([^']+)'\sdo\n(.*?)\nend", re.DOTALL)
    action_pattern = re.compile(r"action\s*(\[\s*:(\w+)(?:\s*,\s*:(\w+))*\s*\]|\s*:(\w+))")
    attribute_pattern = re.compile(r"(\w+)\s+'([^']+)'")

    parsed_data = []

    # Find all resources in the recipe
    resources = resource_pattern.findall(contents)

    for resource in resources:
        resource_type, resource_name, resource_body = resource
        resource_dict = {"type": resource_type, "name": resource_name, "attributes": {}}

        # Extract the action(s)
        action_match = action_pattern.search(resource_body)
        if action_match:
            _action_match = re.sub(r"([\[\]:])", "", action_match.group(1))
            actions = [action.strip() for action in _action_match.split(",")]
            resource_dict["action"] = actions

        # Extract other attributes (e.g., content, mode, owner)
        attributes = attribute_pattern.findall(resource_body)
        for attr_name, attr_value in attributes:
            resource_dict["attributes"][attr_name] = attr_value

        parsed_data.append(resource_dict)

    return parsed_data
