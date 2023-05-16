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


def test_pip_playbook_to_sls(tmp_path):
    """
    Test converting a pip playbook to sls file
    """
    playbook = tmp_path / "pip-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "unarchive": {
                                "dest": "/var/lib/foo",
                                "src": "https://example.com/server-1.2.3.tar.lzma",
                            },
                            "name": "Extract archive into /var/lib/foo",
                        }
                    ],
                    "hosts": "pocminion",
                    "remote_user": "root",
                    "name": "Extract archive",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {
        "Extract archive into /var/lib/foo": {
            "archive.extracted": [
                {"source": "https://example.com/server-1.2.3.tar.lzma"},
                {"name": "/var/lib/foo"},
            ]
        }
    }
