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


def test_user_group_playbook_to_sls(tmp_path):
    """
    Test converting a user and group playbook
    to sls file
    """
    playbook = tmp_path / "user-playbook.yml"

    with open(file=playbook, mode="w", encoding=locale.getpreferredencoding()) as fp_:
        yaml.dump(
            [
              {
                "tasks": [
                  {
                    "ansible.builtin.group": {
                      "state": "present", 
                      "name": "admin"
                    }, 
                    "name": "Add \"admin\" group"
                  }, 
                  {
                    "ansible.builtin.user": {
                      "comment": "Sally Joe", 
                      "group": "admin", 
                      "name": "sally", 
                      "uid": 1041
                    }, 
                    "name": "Add user \"sally\""
                  }
                ], 
                "hosts": "pocminion", 
                "remote_user": "root", 
                "name": "Add user and group"
              }
            ], fp_)

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(file=sls_file, encoding=locale.getpreferredencoding()) as fp_:
        ret = yaml.safe_load(fp_)

    assert ret == {'Add "admin" group': {'group.present': [{'groups': 'admin'}]}, 'Add user "sally"': {'user.present': [{'users': 'sally'}]}}
