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


def test_cmd_playbook_to_sls(tmp_path):
    """
    Test converting a cmd playbook to sls file
    """
    playbook = tmp_path / "cmd-playbook.yml"
    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "ansible.builtin.command": {"cmd": "/usr/bin/command"},
                            "name": "Run command",
                        }
                    ],
                    "hosts": "pocminion",
                    "remote_user": "root",
                    "name": "Test cmd module",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {"Run command": {"cmd.run": [{"name": "/usr/bin/command"}]}}
