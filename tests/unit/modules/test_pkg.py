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


def test_pkg_playbook_to_sls(tmp_path):
    """
    Test converting a pkg playbook
    to sls file
    """
    playbook = tmp_path / "service-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "postgresql latest version",
                            "ansible.builtin.yum": {"state": "latest", "name": "postgresql"},
                        },
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

    assert ret == {"postgresql latest version": {"pkg.latest": [{"pkgs": "postgresql"}]}}


def test_pkg_playbook_to_sls_with_items(tmp_path):
    """
    Test converting a pkg playbook
    to sls file with with_items lookup function
    """
    playbook = tmp_path / "service-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "postgresql latest version",
                            "ansible.builtin.yum": {"state": "latest", "name": "{{ item }}"},
                            "with_items": ["httpd", "php", "php-mysql", "git"],
                        },
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
        "postgresql latest version": {
            "pkg.latest": [{"pkgs": ["httpd", "php", "php-mysql", "git"]}]
        }
    }


def test_pkg_playbook_to_sls_apt_string(tmp_path):
    """
    Test converting a pkg playbook
    to sls file
    """
    playbook = tmp_path / "service-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "postgresql latest version",
                            "ansible.builtin.apt": "name=postgresql update_cache=yes state=latest force_apt_get=yes",
                        },
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

    assert ret == {"postgresql latest version": {"pkg.latest": [{"pkgs": "postgresql"}]}}


def test_pkg_playbook_to_sls_apt_dict(tmp_path):
    """
    Test converting a pkg playbook
    to sls file
    """
    playbook = tmp_path / "service-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "postgresql latest version",
                            "ansible.builtin.apt": {
                                "state": "latest",
                                "name": "postgresql",
                                "update_cache": "yes",
                                "force_apt_get": "yes",
                            },
                        },
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

    assert ret == {"postgresql latest version": {"pkg.latest": [{"pkgs": "postgresql"}]}}
