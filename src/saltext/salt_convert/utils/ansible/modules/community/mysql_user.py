# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import inspect

try:
    import salt.states.mysql_user

    MYSQL_STATE_AVAILABLE = True
except ImportError:
    MYSQL_STATE_AVAILABLE = False

import saltext.salt_convert.utils.ansible.helpers as helpers
import saltext.salt_convert.utils.inspect
import saltext.salt_convert.utils.ansible.lookup as lookup_builtins


def _setup():
    """
    Return the builtins this module should support",
    """
    if MYSQL_STATE_AVAILABLE:
        return ["mysql_user", "community.mysql.mysql_user"]
    else:
        return []


@lookup_builtins.lookup_decorator
@helpers.process_vars_decorator
def process(builtin_data, task, var_data=None):
    """
    Process tasks into Salt states
    """
    # Using 'state' when the ansible module does not use
    # state as an arg
    state = "false"
    state_args = []
    mysql_user_states = {"present": "mysql_user.present", "absent": "mysql_user.absent"}
    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    match_args = {
        "name": "name",
        "password": "password",
        "host": "host",
        "login_user": "connection_user",
        "login_password": "connection_pass",
    }

    state = builtin_data.get("state")
    if not state:
        state = "present"

    _, _func = mysql_user_states[state].split(".")
    salt_args = saltext.salt_convert.utils.inspect.function_args(
        salt.states.mysql_user,
        _func,
        builtin_data,
    )

    for _arg in salt_args:
        if _arg in builtin_data:
            if not [x for x in state_args if _arg in x]:
                state_args.append({_arg: builtin_data[_arg]})

    for _arg in match_args:
        if _arg in builtin_data:
            if not [x for x in state_args if _arg in x]:
                state_args.append({match_args[_arg]: builtin_data[_arg]})

    state_contents = {mysql_user_states[state]: state_args}
    return state_contents
