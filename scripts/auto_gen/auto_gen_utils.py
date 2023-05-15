# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
"""
Module for auto generating the utils files
for each given ansible module

.. versionadded:: 0.0.1

"""
import argparse
import importlib
import inspect
import logging
import pathlib

import salt.utils.files  # pylint: disable=import-error
import yaml
from jinja2 import Environment
from jinja2 import FileSystemLoader


log = logging.getLogger(__name__)


def _render_jinja(template_path=None, context=None):
    """
    Render the jinja logic in utils_code.py.template
    """
    environment = Environment(
        variable_start_string="<{",
        variable_end_string=">}",
        loader=FileSystemLoader(template_path.parent),
    )
    template = environment.get_template(template_path.name)
    content = template.render({"state": False})
    return content


def gen_code(map_file=None, module=None, force=False):
    """
    Generate the code for converting a config system's
    logic into saltconvert's utils modules directory
    """
    utils_path = (
        pathlib.Path(__file__).absolute().parent.parent.parent
        / "src"
        / "saltext"
        / "salt_convert"
        / "utils"
        / "modules"
    )
    if not map_file:
        map_file = pathlib.Path(__file__).parent.parent / "map_file.yml"
    with open(map_file) as fp_:
        data = yaml.safe_load(fp_)
    if module:
        data = {module: data.get(module)}
    for state_name in data.keys():
        module_name = state_name + ".py"
        module_path = utils_path / module_name
        context = {"state": True}

        # Do not auto generate if the file already exists
        if state_name == module and not force:
            if module_path.exists():
                print(
                    f"The module {module} already has been generating. Skipping. "
                    "Please use --force to force auto generation of this module"
                )
                continue

        modules = data[state_name]["modules"]
        functions = data[state_name]["functions"]
        manual_args = data[state_name].get("manual_args")

        other_module = modules[[x for x in modules.keys() if x != "salt"][0]]
        other_name = other_module.split(".")[-1]
        salt_module = modules["salt"]
        import_salt_mod = importlib.import_module(salt_module)
        import_other_mod = importlib.import_module(other_module)
        non_match = []
        arg_map = {}
        for other_func, salt_func in functions.items():
            if not other_func:
                context["state"] = False
            salt_inspect = inspect.signature(getattr(import_salt_mod, salt_func.split(".")[-1]))
            salt_params = salt_inspect.parameters

            other_params = yaml.safe_load(import_other_mod.DOCUMENTATION)["options"].keys()
            for param in other_params:
                if not salt_params.get(param):
                    non_match.append(param)
                else:
                    arg_map[param] = param

        # Add any manual args set in the map file
        # to the args set into the utils module
        if manual_args:
            for key, value in manual_args.items():
                arg_map[key] = value
        func_map = functions
        template = pathlib.Path(__file__).parent / "utils_code.py.template"
        # Render Jinja
        content = _render_jinja(template, context=context)
        # Render string formatting
        content = content.format(
            other_name=other_name, state_name=state_name, func_map=func_map, arg_map=arg_map
        )

        with salt.utils.files.fopen(str(utils_path / module_name), "w") as fp_:
            fp_.write(content)

        if non_match:
            print(
                "The following params did not match any Salt params, you will "
                "need to add the Salt equivalent manually: "
                f'{" ,".join(non_match)}'
            )
        print({"Auto generated code to file": str(utils_path / module_name)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Auto generate the utils modules code from other config systems"
    )
    parser.add_argument(
        "-p", "--path", help="Path to map file that defines the modules and functions"
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force each file to be generated, even if its previously been created",
    )
    parser.add_argument(
        "-m", "--module", help="Specify which module you want to generate from the map file"
    )
    args = parser.parse_args()
    map_file = args.path
    if not map_file:
        map_file = pathlib.Path(__file__).parent / "map_file.yml"
    gen_code(map_file=map_file, module=args.module, force=args.force)
