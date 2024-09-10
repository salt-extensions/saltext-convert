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


def process(builtin_data, lookup_data, task=None):
    """
    Handle lookup builtin items
    """
    module = [x for x in task.keys()][0]
    support_lists = [
        "pkg",
        "yum",
        "ansible.builtin.yum",
        "dnf",
        "ansible.builtin.dnf",
        "apt",
        "ansible.builtin.apt",
    ]
    if isinstance(builtin_data, dict):
        value = "{{ item }}"
        key_list = [key for key, val in builtin_data.items() if val == value]
        for key in key_list:
            if isinstance(lookup_data, list) and module not in support_lists:
                builtin_list = []
                for name in lookup_data:
                    builtin_copy = builtin_data.copy()
                    builtin_copy[key] = name
                    builtin_list.append(builtin_copy)
                builtin_data = builtin_list
            else:
                builtin_data[key] = lookup_data
    elif isinstance(builtin_data, str):
        value = "{{ item }}"
        lookup_data_str = ",".join(lookup_data)
        builtin_data = re.sub(value, lookup_data_str, builtin_data)
    return builtin_data
