# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file for groups

.. versionadded:: 0.0.1

"""
import saltext.salt_convert.utils.lookup as lookup_builtins


def _setup():
    """
    Return the builtins this module should support
    """
    return ["ansible.builtin.group"]


@lookup_builtins.lookup_decorator
def process(builtin_data, task):
    """
    Process tasks into Salt states
    """
    group_states = {"present": "group.present", "absent": "group.absent"}

    state_contents = {group_states[builtin_data["state"]]: [{"groups": builtin_data["name"]}]}
    return state_contents
