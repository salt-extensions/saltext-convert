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


def test_cron_playbook_to_sls(tmp_path):
    """
    Test converting a cron playbook
    to sls file
    """
    playbook = tmp_path / "service-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "name": "Set cron job",
                    "ansible.builtin.cron": {
                        "job": "ls -alh > /dev/null",
                        "name": "check dirs",
                        "minute": "0",
                        "hour": "5,2",
                    },
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
        "Set cron job": {
            "cron.present": [
                {"minute": "0"},
                {"hour": "5,2"},
                {"comment": "check dirs"},
                {"name": "ls -alh > /dev/null"},
            ]
        }
    }
