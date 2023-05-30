# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=import-error
import pathlib

import pytest
import salt.runners.state as state_mod_runner
import saltext.salt_convert.runners.salt_convert as salt_convert_runner

# pylint: enable=import-error


pytestmark = [
    pytest.mark.skip_on_windows,
]


@pytest.fixture
def configure_loader_modules(minion_opts):
    opts = minion_opts.copy()

    return {
        salt_convert_runner: {
            "__opts__": opts,
        },
        state_mod_runner: {
            "__opts__": opts,
        },
    }


def test_full_example_with_vars():
    """
    test a full playbook example
    and ensure salt can call it
    """
    path = pathlib.Path(__file__).parent / "files" / "playbook-with-handlers.yml"

    sls_file = salt_convert_runner.files(path=str(path))["Converted playbooks to sls files"][0]

    ret = state_mod_runner.orchestrate_show_sls(
        f"ansible_convert.{pathlib.Path(sls_file).name.split('.')[0]}"
    )

    assert ret["func-tests-minion-opts"]["Restart everything"] == {
        "cmd": [
            {"name": 'echo "this task will restart the web services"'},
            {"listen_in": [{"service": "memcached"}, {"service": "apache"}]},
            "run",
            {"order": 10000},
        ],
        "__sls__": "ansible_convert.playbook-with-handlers",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Restart memcached"] == {
        "service": [
            {"name": "memcached"},
            "running",
            {"order": 10001},
        ],
        "__sls__": "ansible_convert.playbook-with-handlers",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Restart apache"] == {
        "service": [
            {"name": "apache"},
            "running",
            {"order": 10002},
        ],
        "__sls__": "ansible_convert.playbook-with-handlers",
        "__env__": "base",
    }
