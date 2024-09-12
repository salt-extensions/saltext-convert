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


def test_service_playbook_to_sls(tmp_path):
    """
    Test converting a service playbook
    to sls file
    """
    playbook = tmp_path / "service-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "ansible.builtin.service": {"state": "started", "name": "postgresql"},
                            "name": "Ensure that postgresql is started",
                        }
                    ],
                    "hosts": "databases",
                    "remote_user": "root",
                    "name": "db servers",
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
        "Ensure that postgresql is started": {"service.running": [{"name": "postgresql"}]}
    }
