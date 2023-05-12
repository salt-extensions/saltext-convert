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
    return ["yum", "ansible.builtin.yum", "ansible.builtin.dnf", "dnf"]


@lookup_builtin.lookup_decorator
def process(builtin_data, task):
    """
    Process tasks into Salt states
    """
    pkg_states = {"present": "pkg.installed", "latest": "pkg.latest", "absent": "pkg.removed"}

    state_contents = {pkg_states[builtin_data["state"]]: [{"pkgs": builtin_data["name"]}]}
    return state_contents
