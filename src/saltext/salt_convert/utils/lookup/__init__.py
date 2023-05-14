# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Built in helper functions

.. versionadded:: 0.0.1

"""
import importlib
import os
import pathlib


def _setup_lookup_modules():
    """
    Load the utility modules
    """
    lookup_builtins = {}
    utils_path = pathlib.Path(__file__).parent
    for util_path in os.listdir(utils_path):
        fname, ext = os.path.splitext(util_path)
        if ext == ".py" and not fname.startswith("."):
            mod_name = f"saltext.salt_convert.utils.lookup.{fname}"
            imported_mod = importlib.import_module(mod_name)
            if hasattr(imported_mod, "_setup"):
                mods = imported_mod._setup()
                for _mod in mods:
                    lookup_builtins[_mod] = imported_mod.process
    return lookup_builtins


def lookup_decorator(func):
    def wrapper(builtin_data, task):
        lookup_builtins = _setup_lookup_modules()
        for item in task:
            if item in lookup_builtins:
                lookup_data = task[item]
                builtin_data = lookup_builtins[item](builtin_data, lookup_data)
        return func(builtin_data, task)

    return wrapper
