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


def test_script_playbook_to_sls(tmp_path):
    """
    Test converting a script playbook to sls file
    """
    playbook = tmp_path / "script-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [{"name": "Run script", "script": {"cmd": "/script.sh --arg 1234"}}],
                    "hosts": "pocminion",
                    "remote_user": "root",
                    "name": "Test cmd script",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.ansible_files(path=playbook)["Converted playbooks to sls files"][
        0
    ]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {"Run script": {"cmd.script": [{"name": "/script.sh --arg 1234"}]}}
