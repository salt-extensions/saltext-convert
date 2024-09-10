# Copyright 2023 VMware, Inc.
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
    return ["service", "ansible.builtin.service"]


@lookup_builtins.lookup_decorator
@helpers.process_vars_decorator
def process(builtin_data, task, vars_data):
    """
    Process tasks into Salt states
    """
    service_states = {
        "started": "service.running",
        "stopped": "service.dead",
        "restarted": "service.running",
        "reloaded": "service.running",
    }

    if "enabled" in builtin_data:
        state_contents = {
            service_states[builtin_data["state"]]: [
                {"name": builtin_data["name"]},
                {"enable": builtin_data["enabled"]},
            ]
        }
    else:
        state_contents = {service_states[builtin_data["state"]]: [{"name": builtin_data["name"]}]}
    return state_contents
