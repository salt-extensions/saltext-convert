# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for procssing with_items lookup

.. versionadded:: 0.0.1

"""
import re


def _setup():
    """
    Return the builtins this module should support
    """
    return ["with_items", "loop"]


def process(builtin_data, lookup_data):
    """
    Handle lookup builtin items
    """
    if isinstance(builtin_data, dict):
        value = "{{ item }}"
        key_list = [key for key, val in builtin_data.items() if val == value]
        for key in key_list:
            builtin_data[key] = lookup_data
    elif isinstance(builtin_data, str):
        value = "{{ item }}"
        lookup_data_str = ",".join(lookup_data)
        builtin_data = re.sub(value, lookup_data_str, builtin_data)
    return builtin_data
