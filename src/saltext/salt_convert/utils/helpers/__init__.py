# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Built in helper functions

.. versionadded:: 0.0.1

"""
import copy
import re


def process_vars_decorator(func):
    def wrapper(builtin_data, task, vars_data):
        if isinstance(builtin_data, dict):
            for item in copy.deepcopy(builtin_data):
                for context in vars_data:
                    loaded_vars = vars_data[context]["data"]
                    for loaded_var in loaded_vars:
                        if f"{{ {loaded_var} }}" in builtin_data[item]:
                            updated_var = f'{context}["{loaded_var}"]'
                            builtin_data[item] = re.sub(loaded_var, updated_var, builtin_data[item])
        elif isinstance(builtin_data, str):
            for context in vars_data:
                loaded_vars = vars_data[context]["data"]
                for loaded_var in loaded_vars:
                    if f"{{ {loaded_var} }}" in builtin_data:
                        updated_var = f'{context}["{loaded_var}"]'
                        builtin_data = re.sub(loaded_var, updated_var, builtin_data)
        return func(builtin_data, task, vars_data)

    return wrapper
