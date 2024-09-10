# SPDX-License-Identifier: Apache-2.0
"""
Module for converting state file

.. versionadded:: 0.0.1

"""


def _setup():
    """
    Return the builtins this module should support
    """
    return [
        "package",
    ]


def process(builtin_data):
    """
    Process into Salt states
    """
    pkg_states = {
        "install": "pkg.installed",
        "purge": "pkg.purged",
        "remove": "pkg.removed",
        "upgraded": "pkg.latest",
    }

    for action in builtin_data["action"]:
        state_contents = {pkg_states[action]: [{"pkgs": [builtin_data["name"]]}]}
    return state_contents
