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


def test_file_playbook_to_sls_managed(tmp_path):
    """
    Test converting a file playbook
    to sls file
    """
    playbook = tmp_path / "file-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "manage a file",
                            "ansible.builtin.file": {"path": "/etc/foo.conf",
                                                     "owner": "foo",
                                                     "group": "foo",
                                                     "mode": "0644",
                            },
                        },
                    ],
                    "hosts": "fileservers",
                    "remote_user": "root",
                    "name": "manage files",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {'manage a file': {'file.managed': [{'group': 'foo'},
                                                      {'mode': '0644'},
                                                      {'user': 'foo'},
                                                      {'name': '/etc/foo.conf'}]}}


def test_file_playbook_to_sls_symlink(tmp_path):
    """
    Test converting a file playbook
    to sls file
    """
    playbook = tmp_path / "file-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "manage a file",
                            "ansible.builtin.file": {"state": "link",
                                                     "src": "/file/to/link/to",
                                                     "dest": "/path/to/symlink",
                                                     "owner": "foo",
                                                     "group": "foo",
                            },
                        },
                    ],
                    "hosts": "fileservers",
                    "remote_user": "root",
                    "name": "manage files",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {'manage a file': {'file.symlink': [{'group': 'foo'},
                                                      {'user': 'foo'},
                                                      {'name': '/path/to/symlink'},
                                                      {'target': '/file/to/link/to'}]}}


def test_file_playbook_to_sls_hardlink(tmp_path):
    """
    Test converting a file playbook
    to sls file
    """
    playbook = tmp_path / "file-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "manage a file",
                            "ansible.builtin.file": {"state": "hard",
                                                     "src": "/file/to/link/to",
                                                     "dest": "/path/to/hardlink",
                                                     "owner": "foo",
                                                     "group": "foo",
                            },
                        },
                    ],
                    "hosts": "fileservers",
                    "remote_user": "root",
                    "name": "manage files",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {'manage a file': {'file.hardlink': [{'group': 'foo'},
                                                      {'user': 'foo'},
                                                      {'name': '/path/to/hardlink'},
                                                      {'target': '/file/to/link/to'}]}}


def test_file_playbook_to_sls_directory(tmp_path):
    """
    Test converting a file playbook
    to sls file
    """
    playbook = tmp_path / "file-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "manage a file",
                            "ansible.builtin.file": {"state": "directory",
                                                     "path": "/etc/some_directory",
                                                     "owner": "foo",
                                                     "group": "foo",
                                                     "mode": "0755",
                            },
                        },
                    ],
                    "hosts": "fileservers",
                    "remote_user": "root",
                    "name": "manage files",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {'manage a file': {'file.directory': [{'group': 'foo'},
                                                        {'user': 'foo'},
                                                        {'name': '/etc/some_directory'},
                                                        {"dir_mode": "0755"}]}}

def test_file_playbook_to_sls_touch(tmp_path):
    """
    Test converting a file playbook
    to sls file
    """
    playbook = tmp_path / "file-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "manage a file",
                            "ansible.builtin.file": {"state": "touch",
                                                     "path": "/etc/foo.conf",
                            },
                        },
                    ],
                    "hosts": "fileservers",
                    "remote_user": "root",
                    "name": "manage files",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]

    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {'manage a file': {'file.touch': [{'name': '/etc/foo.conf'}]}}
    playbook = tmp_path / "file-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
                {
                    "tasks": [
                        {
                            "name": "manage a file",
                            "ansible.builtin.file": {"state": "touch",
                                                     "path": "/etc/foo.conf",
                                                     "mode": "0755",
                            },
                        },
                    ],
                    "hosts": "fileservers",
                    "remote_user": "root",
                    "name": "manage files",
                }
            ],
            fp_,
        )

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {'manage a file': {'file.managed': [{"mode": "0755"},
                                                      {'name': '/etc/foo.conf'}]}}
