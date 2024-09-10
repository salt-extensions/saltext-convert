import locale

import pytest  # pylint: disable=3rd-party-module-not-gated
import saltext.salt_convert.runners.salt_convert as salt_convert_runner
import yaml  # pylint: disable=3rd-party-module-not-gated


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

    with open(
        file=playbook, mode="w", encoding=locale.getpreferredencoding()
    ) as fp_:  # pylint: disable=resource-leakage
        yaml.dump(
            [
                {
                    "ansible.builtin.apt_repository": {
                        "repo": "deb http://archive.canonical.com/ubuntu hardy partner",
                        "state": "present",
                    },
                    "name": "Add specified repository into sources list",
                },
                {
                    "name": "Add repository",
                    "ansible.builtin.yum_repository": {
                        "description": "EPEL YUM repo",
                        "name": "epel",
                        "baseurl": "https://download.fedoraproject.org/pub/epel/$releasever/$basearch/",
                    },
                },
            ],
            fp_,
        )

    sls_file = salt_convert_runner.ansible_files(path=playbook)["Converted playbooks to sls files"][
        0
    ]
    with open(
        file=sls_file, encoding=locale.getpreferredencoding()
    ) as fp_:  # pylint: disable=resource-leakage
        ret = yaml.safe_load(fp_)

    assert ret == {
        "Add repository": {
            "pkgrepo.managed": [
                {"name": "epel"},
                {"humanname": "EPEL YUM repo"},
                {"baseurl": "https://download.fedoraproject.org/pub/epel/$releasever/$basearch/"},
            ]
        },
        "Add specified repository into sources list": {
            "pkgrepo.managed": [{"name": "deb http://archive.canonical.com/ubuntu hardy partner"}]
        },
    }
