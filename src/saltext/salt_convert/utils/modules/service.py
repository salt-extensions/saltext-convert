# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""
import saltext.salt_convert.utils.lookup.builtins as lookup_builtin


def _setup():
    """
    Return the builtins this module should support
    """
    return ["service", "ansible.builtin.service"]


def process(builtin_data, task):
    """
    Process tasks into Salt states
    """
    service_states = {"started": "service.running", "stopped": "service.dead"}

    for item in task:
        if item in lookup_builtin.LOOKUP_BUILTINS:
            lookup_data = task[item]
            lookup_builtin.LOOKUP_BUILTINS[item](builtin_data, lookup_data)

    if "enabled" in builtin_data:
        state_contents = {
            service_states[builtin_data["state"]]: [
                {"name": builtin_data["name"], "enable": builtin_data["enabled"]}
            ]
        }
    else:
        state_contents = {service_states[builtin_data["state"]]: [{"name": builtin_data["name"]}]}
    return state_contents
