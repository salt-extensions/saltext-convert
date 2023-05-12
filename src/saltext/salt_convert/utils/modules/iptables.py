# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import inspect

import salt.states.iptables
import saltext.salt_convert.utils.inspect
import saltext.salt_convert.utils.lookup.builtins as lookup_builtin


def _setup():
    """
    Return the builtins this module should support
    """
    return ["ansible.builtin.iptables", "iptables"]


def process(builtin_data, task):
    """
    Process tasks into Salt states
    """
    state_args = []
    iptables_states = {"present": "iptables.append", "absent": "iptables.delete"}
    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    match_args = {"chain": "chain", "source": "source", "jump": "jump"}

    for item in task:
        if item in lookup_builtin.LOOKUP_BUILTINS:
            lookup_data = task[item]
            lookup_builtin.LOOKUP_BUILTINS[item](builtin_data, lookup_data)

    state = builtin_data.get("state")

    if not state:
        state = "present"
    _, _func = iptables_states[state].split(".")
    salt_args = saltext.salt_convert.utils.inspect.function_args(
        salt.states.iptables, _func, builtin_data
    )

    for _arg in salt_args:
        if _arg in builtin_data:
            state_args.append({_arg: builtin_data[_arg]})

    for _arg in match_args:
        if _arg in builtin_data:
            state_args.append({match_args[_arg]: builtin_data[_arg]})

    state_contents = {iptables_states[state]: state_args}
    return state_contents
