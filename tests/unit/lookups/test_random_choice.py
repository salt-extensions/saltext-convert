"""
testing lookup random choice
"""
import locale

import pytest
import saltext.salt_convert.runners.salt_convert as salt_convert_runner
import yaml


@pytest.fixture
def configure_loader_modules(tmp_path):
    """
    tmp file setup
    """
    return {
        salt_convert_runner: {
            "__opts__": {"file_roots": {"base": [str(tmp_path / "root")]}},
        },
    }


def test_lookup_with_random_choice(tmp_path):
    """
    Test converting with_random_choice into jinja
    """
    playbook = tmp_path / "playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as _fd:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "random install",
                            "ansible.builtin.yum": {"state": "latest", "name": "{{ item }}"},
                            "with_random_choice": ["pkg1", "pkg2", "pkg3"],
                        },
                    ],
                    "hosts": "databases",
                    "remote_user": "root",
                    "name": "db things",
                }
            ],
            _fd,
        )

    sls_file = salt_convert_runner.ansible_files(path=playbook)["Converted playbooks to sls files"][
        0
    ]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as _fd:
        ret = yaml.safe_load(_fd)

    assert ret == {
        "random install": {
            "pkg.latest": [{"pkgs": '{{ ["pkg1", "pkg2", "pkg3"] | random_sample(1) | first }}'}]
        }
    }
