# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import salt.states.cmd

import saltext.salt_convert.utils.ansible.helpers as helpers
import saltext.salt_convert.utils.ansible.lookup as lookup_builtins
import saltext.salt_convert.utils.inspect


def _setup():
    """
    Return the builtins this module should support",
    """
    return [
        "command",
        "ansible.builtin.command",
        "shell",
        "ansible.builtin.shell",
        "win_shell",
        "ansible.windows.win_shell",
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
    cmd_states = {"false": "cmd.run"}
    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    match_args = {"cmd": "name", "chdir": "cwd"}

    _, _func = cmd_states[state].split(".")
    if isinstance(builtin_data, dict):
        salt_args = saltext.salt_convert.utils.inspect.function_args(
            salt.states.cmd,
            _func,
            builtin_data,
        )

        for _arg in salt_args:
            if _arg in builtin_data:
                state_args.append({_arg: builtin_data[_arg]})

        for _arg, _val in match_args.items():
            if _arg in builtin_data:
                state_args.append({match_args[_arg]: builtin_data[_arg]})

        state_contents = {cmd_states[state]: state_args}
    else:
        state_args = {"name": builtin_data}
        state_contents = {cmd_states[state]: [state_args]}
    return state_contents
