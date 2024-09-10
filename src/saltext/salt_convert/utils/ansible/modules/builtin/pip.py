# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import saltext.salt_convert.utils.ansible.helpers as helpers
import saltext.salt_convert.utils.ansible.lookup as lookup_builtins


def _setup():
    """
    Return the builtins this module should support
    """
    return ["pip", "ansible.builtin.pip"]


@lookup_builtins.lookup_decorator
@helpers.process_vars_decorator
def process(builtin_data, task, vars_data):
    """
    Process tasks into Salt states
    """
    pip_states = {"absent": "pip.removed", "present": "pip.installed"}

    state = builtin_data.get("state")
    if not state:
        state = "present"
    state_contents = {pip_states[state]: [{"name": builtin_data["name"]}]}
    return state_contents
