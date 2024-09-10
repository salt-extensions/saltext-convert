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
    return [
        "yum",
        "ansible.builtin.yum",
        "ansible.builtin.dnf",
        "dnf",
        "apt",
        "ansible.builtin.apt",
    ]


@lookup_builtins.lookup_decorator
@helpers.process_vars_decorator
def process(builtin_data, task, vars_data):
    """
    Process tasks into Salt states
    """
    pkg_states = {"present": "pkg.installed", "latest": "pkg.latest", "absent": "pkg.removed"}

    if "apt" in task or "ansible.builtin.apt" in task:
        state_contents = _process_apt(pkg_states, builtin_data, task)
    else:
        state_contents = {pkg_states[builtin_data["state"]]: [{"pkgs": builtin_data["name"]}]}
    return state_contents


def _process_apt(pkg_states, builtin_data, task):
    """
    Process tasks into Salt states for apt
    """
    if isinstance(builtin_data, str):
        apt_args = builtin_data.split()

        apt_args_dict = {item[0]: item[1] for item in [arg.split("=") for arg in apt_args]}

        _pkgs = apt_args_dict["name"].split(",")
        if len(_pkgs) == 1:
            _pkgs = _pkgs[0]
        state_contents = {pkg_states[apt_args_dict["state"]]: [{"pkgs": _pkgs}]}
    else:
        state_contents = {pkg_states[builtin_data["state"]]: [{"pkgs": builtin_data["name"]}]}
    return state_contents
