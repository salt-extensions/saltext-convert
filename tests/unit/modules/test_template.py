import locale

import pytest
import yaml

import saltext.salt_convert.runners.salt_convert as salt_convert_runner


@pytest.fixture
def configure_loader_modules(tmp_path):
    return {
        salt_convert_runner: {
            "__opts__": {"file_roots": {"base": [str(tmp_path / "root")]}},
        },
    }


def test_file_playbook_to_sls_managed(tmp_path):
    """
    Test converting a file playbook
    to sls file
    """
    playbook = tmp_path / "file-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "manage a file",
                            "ansible.builtin.template": {
                                "src": "files/apache.conf.j2",
                                "dest": "/etc/apache2/sites-available/my_site.conf",
                            },
                        },
                    ],
                    "hosts": "fileservers",
                    "remote_user": "root",
                    "name": "manage files",
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
        "manage a file": {
            "file.managed": [
                {"name": "/etc/apache2/sites-available/my_site.conf"},
                {"source": "files/apache.conf.j2"},
            ]
        }
    }
