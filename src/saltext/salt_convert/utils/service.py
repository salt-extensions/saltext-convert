import saltext.salt_convert.utils.lookup.builtins as lookup_builtin


def _setup():
    return ["service",
            "ansible.builtin.service"
            ]


def process(builtin_data, task):
    service_states = {"started": "service.running",
                  "stopped": "service.dead"}

    for item in task:
        if item in lookup_builtin.LOOKUP_BUILTINS:
            lookup_data = task[item]
            ret = globals()[lookup_builtin.LOOKUP_BUILTINS[item]](builtin_data, lookup_data)

    if "enabled" in builtin_data:
        state_contents = {service_states[builtin_data["state"]]: [{"name": builtin_data["name"],
                                                                   "enable": builtin_data["enabled"]}]}
    else:
        state_contents = {service_states[builtin_data["state"]]: [{"name": builtin_data["name"]}]}
    return state_contents


