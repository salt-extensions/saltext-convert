# Copyright 2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
import pathlib


def test_full_example(salt_run_cli, salt_call_cli):
    """
    test a full playbook example
    and ensure salt can call it
    """
    path = pathlib.Path(__file__).parent / "files" / "full-playbook-example.yml"
    sls_file = salt_run_cli.run("convert.files", path=str(path)).json[
        "Converted playbooks to sls files"
    ][0]
    ret = salt_call_cli.run(
        "state.show_sls", f"ansible_convert.{pathlib.Path(sls_file).name.strip('.sls')}"
    )

    assert ret.json["Configure SELinux"] == {
        "selinux": [
            {"name": "httpd_can_network_connect_db"},
            {"value": True},
            {"persist": True},
            "boolean",
            {"order": 10000},
        ],
        "__sls__": "ansible_convert.full-playbook-example",
        "__env__": "base",
    }

    assert ret.json["Install packages"] == {
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
            {"order": 10001},
        ],
        "__sls__": "ansible_convert.full-playbook-example",
        "__env__": "base",
    }
    assert ret.json["http service"] == {
        "service": [{"name": "httpd"}, {"enable": True}, "running", {"order": 10002}],
        "__sls__": "ansible_convert.full-playbook-example",
        "__env__": "base",
    }
