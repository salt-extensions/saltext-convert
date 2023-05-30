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
    path = pathlib.Path(__file__).parent / "files" / "full-playbook-example-with-vars.yml"

    sls_file = salt_convert_runner.files(path=str(path))["Converted playbooks to sls files"][0]

    ret = state_mod_runner.orchestrate_show_sls(
        f"ansible_convert.{pathlib.Path(sls_file).name.split('.')[0]}"
    )

    assert ret["func-tests-minion-opts"]["Install prerequisites"] == {
        "pkg": [
            {"pkgs": "aptitude"},
            "latest",
            {"order": 10000},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Install LAMP Packages"] == {
        "pkg": [
            {
                "pkgs": [
                    "apache2",
                    "mysql-server",
                    "python3-pymysql",
                    "php",
                    "php-mysql",
                    "libapache2-mod-php",
                ]
            },
            "latest",
            {"order": 10001},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Create document root"] == {
        "file": [
            {"user": "sammy"},
            {"name": "/var/www/your_domain"},
            {"dir_mode": "0755"},
            "directory",
            {"order": 10002},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Set up Apache virtualhost"] == {
        "file": [
            {"name": "/etc/apache2/sites-available/your_domain.conf"},
            {"source": "files/apache.conf.j2"},
            "managed",
            {"order": 10003},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Enable new site"] == {
        "cmd": [
            {"name": "/usr/sbin/a2ensite your_domain.conf"},
            "run",
            {"order": 10004},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Disable default Apache site"] == {
        "cmd": [
            {"name": "/usr/sbin/a2dissite 000-default.conf"},
            "run",
            {"order": 10005},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Sets the root password"] == {
        "mysql_user": [
            {"name": "root"},
            {"password": "mysql_root_password"},
            "present",
            {"order": 10006},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Removes all anonymous user accounts"] == {
        "mysql_user": [
            {"name": ""},
            {"connection_user": "root"},
            {"connection_pass": "mysql_root_password"},
            "absent",
            {"order": 10007},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Removes the MySQL test database"] == {
        "mysql_db": [
            {"name": "test"},
            {"connection_user": "root"},
            {"connection_pass": "mysql_root_password"},
            "absent",
            {"order": 10008},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }

    assert ret["func-tests-minion-opts"]["Sets Up PHP Info Page"] == {
        "file": [
            {"name": "/var/www/your_domain/info.php"},
            {"source": "files/info.php.j2"},
            "managed",
            {"order": 10009},
        ],
        "__sls__": "ansible_convert.full-playbook-example-with-vars",
        "__env__": "base",
    }
