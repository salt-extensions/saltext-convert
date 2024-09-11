import locale

import pytest
import saltext.salt_convert.runners.salt_convert as salt_convert_runner
import yaml


@pytest.fixture
def configure_loader_modules(tmp_path):
    return {
        salt_convert_runner: {
            "__opts__": {"file_roots": {"base": [str(tmp_path / "root")]}},
        },
    }


def test_mysql_playbook_to_sls_managed(tmp_path):
    """
    Test converting a file playbook
    to sls file
    """
    playbook = tmp_path / "mysql-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "manage a mysql db",
                            "community.mysql.mysql_db": {
                                "name": "test",
                                "state": "present",
                                "login_user": "root",
                                "login_password": "mysql_root_password",
                            },
                        },
                    ],
                    "hosts": "dbservers",
                    "remote_user": "root",
                    "name": "manage database database",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.ansible_files(path=playbook)["Converted playbooks to sls files"][
        0
    ]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

        assert ret == {
            "manage a mysql db": {
                "mysql_db.present": [
                    {"name": "test"},
                    {"connection_user": "root"},
                    {"connection_pass": "mysql_root_password"},
                ]
            }
        }
