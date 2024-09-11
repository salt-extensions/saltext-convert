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


def test_docker_container_present(tmp_path):
    """
    Test converting a file playbook
    to sls file
    """
    playbook = tmp_path / "docker-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "manage a docker container",
                            "community.docker.docker_container": {
                                "name": "mycontainer",
                                "image": "ubuntu:14.04",
                                "state": "present",
                            },
                        },
                    ],
                    "hosts": "servers",
                    "remote_user": "root",
                    "name": "manage docker container",
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
        "manage a docker container": {
            "docker_container.running": [{"name": "mycontainer"}, {"image": "ubuntu:14.04"}]
        }
    }


def test_docker_container_absent(tmp_path):
    """
    Test converting a file playbook
    to sls file
    """
    playbook = tmp_path / "docker-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "remove a docker container",
                            "community.docker.docker_container": {
                                "name": "mycontainer",
                                "state": "absent",
                            },
                        },
                    ],
                    "hosts": "servers",
                    "remote_user": "root",
                    "name": "manage docker container",
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
        "remove a docker container": {"docker_container.absent": [{"name": "mycontainer"}]}
    }
