# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Built in helper functions

.. versionadded:: 0.0.1

"""


def lookup_decorator(func):
    def wrapper(builtin_data, task):
        for item in task:
            if item in LOOKUP_BUILTINS:
                lookup_data = task[item]
                LOOKUP_BUILTINS[item](builtin_data, lookup_data)
        return func(builtin_data, task)

    return wrapper


def process_with_items(builtin_data, lookup_data):
    """
    Handle lookup builtin items
    """
    value = "{{ item }}"
    key_list = [key for key, val in builtin_data.items() if val == value]
    for key in key_list:
        builtin_data[key] = lookup_data
    return builtin_data


LOOKUP_BUILTINS = {
    "with_items": process_with_items,
}
