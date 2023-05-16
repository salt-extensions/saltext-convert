# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import inspect

import salt.states.file
import saltext.salt_convert.utils.inspect
import saltext.salt_convert.utils.lookup as lookup_builtins


def _setup():
    """
    Return the builtins this module should support
    """
    return [
        "file",
        "ansible.builtin.file",
    ]


@lookup_builtins.lookup_decorator
def process(builtin_data, task):
    """
    Process tasks into Salt states
    """
    state_args = []
    file_states = {
        "file": "file.managed",
        "directory": "file.directory",
        "hard": "file.hardlink",
        "link": "file.symlink",
        "touch": "file.touch",
    }

    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    file_global_args = {"owner": "user", "path": "name", "dest": "name", "src": "target"}

    file_state_args = {"directory": {"mode": "dir_mode"}}

    state = builtin_data.get("state")

    if not state:
        state = "file"

    if state == "touch" and "mode" in builtin_data:
        state = "file"

    _, _func = file_states[state].split(".")
    salt_args = saltext.salt_convert.utils.inspect.function_args(
        salt.states.file, _func, builtin_data
    )

    for _arg in salt_args:
        if _arg in builtin_data:
            state_args.append({_arg: builtin_data[_arg]})

    for _arg in file_global_args:
        if _arg in builtin_data:
            state_args.append({file_global_args[_arg]: builtin_data[_arg]})

    if state in file_state_args:
        for _arg in file_state_args[state]:
            if _arg in builtin_data:
                state_args.append({file_state_args[state][_arg]: builtin_data[_arg]})

    state_contents = {file_states[state]: state_args}
    return state_contents
