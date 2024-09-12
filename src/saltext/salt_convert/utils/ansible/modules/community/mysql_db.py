# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
try:
    import salt.states.mysql_database

    MYSQL_STATE_AVAILABLE = True
except ImportError:
    MYSQL_STATE_AVAILABLE = False

import saltext.salt_convert.utils.ansible.helpers as helpers
import saltext.salt_convert.utils.ansible.lookup as lookup_builtins
import saltext.salt_convert.utils.inspect


def _setup():
    """
    Return the builtins this module should support",
    """
    if MYSQL_STATE_AVAILABLE:
        return ["mysql_db", "community.mysql.mysql_db"]
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
    mysql_db_states = {"present": "mysql_db.present", "absent": "mysql_db.absent"}
    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    match_args = {
        "name": "name",
        "login_user": "connection_user",
        "login_password": "connection_pass",
    }

    state = builtin_data.get("state")
    if not state:
        state = "present"

    _, _func = mysql_db_states[state].split(".")
    salt_args = saltext.salt_convert.utils.inspect.function_args(
        salt.states.mysql_database,
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

    state_contents = {mysql_db_states[state]: state_args}
    return state_contents
