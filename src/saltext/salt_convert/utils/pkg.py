import saltext.salt_convert.utils.lookup.builtins as lookup_builtin


def process_pkg(builtin_data, task):
    pkg_states = {"present": "pkg.installed",
                  "latest": "pkg.latest",
                  "absent": "pkg.removed"}

    for item in task:
        if item in lookup_builtin.LOOKUP_BUILTINS:
            lookup_data = task[item]
            lookgup_builtin.LOOKUP_BUILTINS[item](builtin_data, lookup_data)

    state_contents = {pkg_states[builtin_data["state"]]: [{"pkgs": builtin_data["name"]}]}
    return state_contents
