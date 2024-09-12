# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
try:
    import salt.states.docker_image

    DOCKER_STATE_AVAILABE = True
except ImportError:
    DOCKER_STATE_AVAILABE = False

import saltext.salt_convert.utils.ansible.helpers as helpers
import saltext.salt_convert.utils.ansible.lookup as lookup_builtins
import saltext.salt_convert.utils.inspect


def _setup():
    """
    Return the builtins this module should support",
    """
    if DOCKER_STATE_AVAILABE:
        return ["docker_image", "community.docker.docker_image"]
    return []


@lookup_builtins.lookup_decorator
@helpers.process_vars_decorator
def process(builtin_data, task, vars_data=None):
    """
    Process tasks into Salt states
    """
    # Using 'state' when the ansible module does not use
    # state as an arg
    state = "false"
    state_args = []
    docker_image_states = {"present": "docker_image.present", "absent": "docker_image.absent"}
    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    match_args = {"build": "build", "name": "name", "tag": "tag"}

    state = builtin_data.get("state")
    if not state:
        state = "present"

    _, _func = docker_image_states[state].split(".")
    salt_args = saltext.salt_convert.utils.inspect.function_args(
        salt.states.docker_image,
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

    state_contents = {docker_image_states[state]: state_args}
    return state_contents
