import saltext.salt_convert.utils.lookup.builtins as lookup_builtin


def _setup():
    return ["seboolean",
            "ansible.posix.seboolean"]


def process(builtin_data, task):
    selinux_state = "selinux.boolean"

    for item in task:
        if item in lookup_builtin.LOOKUP_BUILTINS:
            lookup_data = task[item]
            lookup_builtin.LOOKUP_BUILTINS[item](builtin_data, lookup_data)

    if "persistent" in builtin_data:
        state_contents = {selinux_state: [{"name": builtin_data["name"],
                                           "value": builtin_data["state"],
                                           "persist": builtin_data["persistent"]}]}
    else:
        state_contents = {selinux_state: [{"name": builtin_data["name"],
                                           "value": builtin_data["state"]}]}

    return state_contents
