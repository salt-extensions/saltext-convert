# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import saltext.salt_convert.utils.lookup as lookup_builtins


def _setup():
    """
    Return the builtins this module should support
    """
    return ["seboolean", "ansible.posix.seboolean"]


@lookup_builtins.lookup_decorator
def process(builtin_data, task):
    """
    Process tasks into Salt states
    """
    selinux_state = "selinux.boolean"

    if "persistent" in builtin_data:
        state_contents = {
            selinux_state: [
                {
                    "name": builtin_data["name"],
                    "value": builtin_data["state"],
                    "persist": builtin_data["persistent"],
                }
            ]
        }
    else:
        state_contents = {
            selinux_state: [{"name": builtin_data["name"], "value": builtin_data["state"]}]
        }

    return state_contents
