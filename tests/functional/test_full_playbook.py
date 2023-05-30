# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib

import pytest
import saltext.salt_convert.runners.salt_convert as salt_convert_runner


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
    }


def test_full_example(modules):
    """
    test a full playbook example
    and ensure salt can call it
    """
    path = pathlib.Path(__file__).parent / "files" / "full-playbook-example.yml"
    sls_file = salt_convert_runner.files(path=str(path))["Converted playbooks to sls files"][0]
    ret = modules.state.show_sls(f"ansible_convert.{pathlib.Path(sls_file).name.strip('.sls')}")

    assert ret["Install packages"] == {
        "pkg": [
            {
                "pkgs": [
                    "httpd",
                    "php",
                    "php-mysql",
                    "git",
                    "libsemanage-python",
                    "libselinux-python",
                ]
            },
            "installed",
            {"order": 10000},
        ],
        "__sls__": "ansible_convert.full-playbook-example",
        "__env__": "base",
    }

    assert ret["http service"] == {
        "service": [{"name": "httpd"}, {"enable": True}, "running", {"order": 10001}],
        "__sls__": "ansible_convert.full-playbook-example",
        "__env__": "base",
    }

    assert ret["Configure SELinux"] == {
        "selinux": [
            {"name": "httpd_can_network_connect_db"},
            {"value": True},
            {"persist": True},
            "boolean",
            {"order": 10002},
        ],
        "__sls__": "ansible_convert.full-playbook-example",
        "__env__": "base",
    }
