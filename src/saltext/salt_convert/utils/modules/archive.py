# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import inspect

import salt.states.archive
import saltext.salt_convert.utils.helpers as helpers
import saltext.salt_convert.utils.inspect
import saltext.salt_convert.utils.lookup as lookup_builtins


def _setup():
    """
    Return the builtins this module should support",
    """
    return ["unarchive"]


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
    archive_states = {"false": "archive.extracted"}
    # manually add the args that are not automatically inspected further down
    # usually due to **kwargs usage or a mismatch in name
    match_args = {
        "src": "source",
        "dest": "name",
        "extra_opts": "options",
        "validate_certs": "skip_verify",
    }

    _, _func = archive_states[state].split(".")
    salt_args = saltext.salt_convert.utils.inspect.function_args(
        salt.states.archive,
        _func,
        builtin_data,
    )

    for _arg in salt_args:
        if _arg in builtin_data:
            state_args.append({_arg: builtin_data[_arg]})

    for _arg in match_args:
        if _arg in builtin_data:
            state_args.append({match_args[_arg]: builtin_data[_arg]})

    state_contents = {archive_states[state]: state_args}
    return state_contents
