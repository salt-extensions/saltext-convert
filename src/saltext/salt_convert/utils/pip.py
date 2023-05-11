# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import saltext.salt_convert.utils.lookup.builtins as lookup_builtin


def _setup():
    """
    Return the builtins this module should support
    """
    return ["pip", "ansible.builtin.pip"]


def process(builtin_data, task):
    """
    Process tasks into Salt states
    """
    pip_states = {"absent": "pip.removed", "present": "pip.installed"}

    for item in task:
        if item in lookup_builtin.LOOKUP_BUILTINS:
            lookup_data = task[item]
            lookup_builtin.LOOKUP_BUILTINS[item](builtin_data, lookup_data)

    state = builtin_data.get("state")
    if not state:
        state = "present"
    state_contents = {pip_states[state]: [{"name": builtin_data["name"]}]}
    return state_contents
