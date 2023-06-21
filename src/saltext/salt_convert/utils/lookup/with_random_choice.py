# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for procssing with_random_choice lookup

.. versionadded:: 0.0.1

"""
import json


def _setup():
    """
    Return the builtins this module should support
    """
    return ["with_random_choice"]


def process(builtin_data, lookup_data, task=None):
    """
    Handle lookup builtin items
    """
    if isinstance(builtin_data, dict):
        value = "{{ item }}"
        key_list = [key for key, val in builtin_data.items() if val == value]
        for key in key_list:
            builtin_data[key] = f"{{{{ {json.dumps(lookup_data)} | random_sample(1) | first }}}}"
    return builtin_data
