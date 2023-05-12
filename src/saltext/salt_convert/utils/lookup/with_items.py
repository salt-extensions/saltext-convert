# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for procssing with_items lookup

.. versionadded:: 0.0.1

"""


def _setup():
    """
    Return the builtins this module should support
    """
    return ["with_items"]


def process(builtin_data, lookup_data):
    """
    Handle lookup builtin items
    """
    value = "{{ item }}"
    key_list = [key for key, val in builtin_data.items() if val == value]
    for key in key_list:
        builtin_data[key] = lookup_data
    return builtin_data
