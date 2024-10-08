# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import salt.states.file

import saltext.salt_convert.utils.ansible.helpers as helpers
import saltext.salt_convert.utils.ansible.lookup as lookup_builtins
import saltext.salt_convert.utils.inspect


def _setup():
    """
    Return the builtins this module should support
    """
    return [
        "template",
        "ansible.builtin.template",
    ]


@lookup_builtins.lookup_decorator
@helpers.process_vars_decorator
def process(builtin_data, task, vars_data=None):
    """
    Process tasks into Salt states
    """
    state_args = []
    template_states = {
        "template": "file.managed",
    }

    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    template_global_args = {"owner": "user", "path": "name", "dest": "name", "src": "source"}

    state = builtin_data.get("state")

    if not state:
        state = "template"

    _, _func = template_states[state].split(".")
    salt_args = saltext.salt_convert.utils.inspect.function_args(
        salt.states.file, _func, builtin_data
    )

    for _arg in salt_args:
        if _arg in builtin_data:
            state_args.append({_arg: builtin_data[_arg]})

    for _arg, _val in template_global_args.items():
        if _arg in builtin_data:
            state_args.append({template_global_args[_arg]: builtin_data[_arg]})

    state_contents = {template_states[state]: state_args}
    return state_contents
