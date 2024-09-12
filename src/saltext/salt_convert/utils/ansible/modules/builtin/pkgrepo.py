# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import salt.states.pkgrepo

import saltext.salt_convert.utils.ansible.helpers as helpers
import saltext.salt_convert.utils.ansible.lookup as lookup_builtins
import saltext.salt_convert.utils.inspect


def _setup():
    """
    Return the builtins this module should support",
    """
    return [
        "apt_repository",
        "ansible.builtin.apt_repository",
        "ansible.builtin.yum_repository",
        "yum_repository",
    ]


@lookup_builtins.lookup_decorator
@helpers.process_vars_decorator
def process(builtin_data, task, vars_data):
    """
    Process tasks into Salt states
    """
    # Using 'state' when the ansible module does not use
    # state as an arg
    state = "false"
    state_args = []
    pkgrepo_states = {"present": "pkgrepo.managed", "absent": "pkgrepo.absent"}
    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    match_args = {
        "repo": "name",
        "filename": "file",
        "mirrorlist": "mirrorlist",
        "description": "humanname",
        "enabled": "enabled",
        "gpgkey": "gpgkey",
        "baseurl": "baseurl",
    }

    state = builtin_data.get("state")
    if not state:
        state = "present"

    _, _func = pkgrepo_states[state].split(".")
    salt_args = saltext.salt_convert.utils.inspect.function_args(
        salt.states.pkgrepo,
        _func,
        builtin_data,
    )

    for _arg in salt_args:
        if _arg in builtin_data:
            state_args.append({_arg: builtin_data[_arg]})

    for _arg in match_args.items():
        if _arg in builtin_data:
            state_args.append({match_args[_arg]: builtin_data[_arg]})

    state_contents = {pkgrepo_states[state]: state_args}
    return state_contents
