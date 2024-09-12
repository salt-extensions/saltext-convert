# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
try:
    import salt.states.docker_container

    DOCKER_STATE_AVAILABLE = True
except ImportError:
    DOCKER_STATE_AVAILABLE = False

import saltext.salt_convert.utils.ansible.lookup as lookup_builtins
import saltext.salt_convert.utils.inspect


def _setup():
    """
    Return the builtins this module should support",
    """
    if DOCKER_STATE_AVAILABLE:
        return ["docker_container", "community.docker.docker_container"]
    else:
        return []


@lookup_builtins.lookup_decorator
def process(builtin_data, task, vars_data):
    """
    Process tasks into Salt states
    """
    # Using 'state' when the ansible module does not use
    # state as an arg
    state = "false"
    state_args = []
    docker_container_states = {
        "present": "docker_container.running",
        "absent": "docker_container.absent",
    }
    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    match_args = {"image": "image", "name": "name", "networks": "networks"}

    state = builtin_data.get("state")
    if not state:
        state = "present"

    _, _func = docker_container_states[state].split(".")
    salt_args = saltext.salt_convert.utils.inspect.function_args(
        salt.states.docker_container,
        _func,
        builtin_data,
    )

    for _arg in salt_args:
        if _arg in builtin_data:
            if not [x for x in state_args if _arg in x]:
                state_args.append({_arg: builtin_data[_arg]})

    for _arg in match_args.items():
        if _arg in builtin_data:
            if not [x for x in state_args if _arg in x]:
                state_args.append({match_args[_arg]: builtin_data[_arg]})

    state_contents = {docker_container_states[state]: state_args}
    return state_contents
