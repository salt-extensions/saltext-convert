# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file for users

.. versionadded:: 0.0.1

"""
import saltext.salt_convert.utils.lookup as lookup_builtins


def _setup():
    """
    Return the builtins this module should support
    """
    return ["ansible.builtin.user"]


@lookup_builtins.lookup_decorator
def process(builtin_data, task):
    """
    Process tasks into Salt states
    """
    user_states = {"present": "user.present", "absent": "user.absent"}

    state = builtin_data.get("state")
    if not state:
        state = "present"
    state_contents = {user_states[state]: [{"users": builtin_data["name"]}]}
    return state_contents
