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


def test_docker_image_present(tmp_path):
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
                            "name": "manage a docker image",
                            "community.docker.docker_image": {
                                "name": "ubuntu:14.04",
                                "state": "present",
                            },
                        },
                    ],
                    "hosts": "servers",
                    "remote_user": "root",
                    "name": "manage docker image",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {"manage a docker image": {"docker_image.present": [{"name": "ubuntu:14.04"}]}}


def test_docker_image_absent(tmp_path):
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
                            "name": "remove a docker image",
                            "community.docker.docker_image": {
                                "name": "ubuntu:14.04",
                                "state": "absent",
                                "tag": "v1",
                            },
                        },
                    ],
                    "hosts": "servers",
                    "remote_user": "root",
                    "name": "manage docker image",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {
        "remove a docker image": {"docker_image.absent": [{"name": "ubuntu:14.04"}, {"tag": "v1"}]}
    }
