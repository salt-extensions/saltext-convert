import saltext.salt_convert.runners.salt_convert as salt_convert_runner
import yaml


def test_pkg_playbook_to_sls(tmp_path):
    """
    Test converting a pkg playbook
    to sls file
    """
    playbook=tmp_path / "service-playbook.yml"

    with open(playbook, "w") as fp:
        yaml.dump([
         {
           "tasks": [
             {
               "name": "postgresql latest version",
               "ansible.builtin.yum": {
                 "state": "latest",
                 "name": "postgresql"
               }
             },
           ],
           "hosts": "databases",
           "remote_user": "root",
           "name": "db servers"
         }], fp)

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(sls_file, "r") as fp:
        ret = yaml.safe_load(fp)

    assert ret == {'postgresql latest version': {'pkg.latest': [{'pkgs': 'postgresql'}]}}
