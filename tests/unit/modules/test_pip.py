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


def test_pip_playbook_to_sls(tmp_path):
    """
    Test converting a pip playbook to sls file
    """
    playbook = tmp_path / "pip-playbook.yml"

    with open(
        file=playbook, mode="w", encoding=locale.getpreferredencoding()
    ) as fp_:  # pylint: disable=resource-leakage
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "ansible.builtin.pip": {"name": "bottle"},
                            "name": "Install bottle python package",
                        }
                    ],
                    "hosts": "pocminion",
                    "remote_user": "root",
                    "name": "Update web servers",
                }
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

    assert ret == {"Install bottle python package": {"pip.installed": [{"name": "bottle"}]}}
