import yaml
import saltext.salt_convert.runners.salt_convert as salt_convert_runner


def test_service_playbook_to_sls(tmp_path):
    """
    Test converting a service playbook
    to sls file
    """
    playbook=tmp_path / "service-playbook.yml"

    with open(playbook, "w") as fp:
        yaml.dump([
          {
              "tasks": [
                    {"ansible.builtin.service": {
                                      "state": "started",
                                      "name": "postgresql"
                                    },
                     "name": "Ensure that postgresql is started"}
                  ],
              "hosts": "databases",
              "remote_user": "root",
              "name": "db servers"
            }
        ], fp)

    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(sls_file, "r") as fp:
        ret = yaml.safe_load(fp)

    assert ret == {'Ensure that postgresql is started': {'service.running':
                                                         [{'name':
                                                           'postgresql'}]}}
