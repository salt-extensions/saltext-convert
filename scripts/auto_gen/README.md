# auto-gen

Tool to auto generate the utils modules from one config management system to salt.

## Quickstart

To get started auto generating a new module:

    # Create a new venv
    Add the name, the modules and functions of new module to the map_file.yml:
    user:
      modules: {"salt": "salt.states.user", "ansible": "ansible.modules.user"}
      functions: {"present": "user.present", "absent": "user.absent"}

    In the example above the ``functions`` arg is expecting the ansible status of
    ``present`` to be the first key and then Salt's equivalent state function
    to be the value. If the matching ansible module does not use a ``state``
    arg in the module, just add ``false`` as the key. For example the git
    module does not have a ``state` key, and looks like the following:

    git:
      modules: {"salt": "salt.states.git", "ansible": "ansible.modules.git"}
      functions: {"false": "git.cloned"}
      manual_args: {"repo": "name", "dest": "target", "version": "branch"}

    The example above also shows the use of ``manual_args``. For any args
    that the script cannot manually detect you can add the mapping to
    ``manual_args`` so it always gets created anytime you re-run the script.

    # Now you are ready to run the script
    python scripts/auto_gen/auto_gen_utils.py

    This will go through each entry in the map_file.yml file and auto generate the
    code if it does not already exist in the utils/modules path.

    # If you want to only run this script for a specific module you can pass
    # ``--module`` to the script
    python scripts/auto_gen/auto_gen_utils.py --module=pip

    # To run the script and force any module to be auto generated even if it has
    # previously been added to utils/module you need to pass ``-force``
    python scripts/auto_gen/auto_gen_utils.py --force
