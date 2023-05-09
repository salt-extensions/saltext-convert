import yaml
import saltext.salt_convert.runners.salt_convert as salt_convert_runner


def test_selinux_playbook_to_sls(tmp_path):
    """
    Test converting a service playbook
    to sls file
    """
    playbook=tmp_path / "service-playbook.yml"

    with open(playbook, "w") as fp:
        yaml.dump(
          [
            {
              "name": "Set httpd_can_network_connect", 
              "ansible.posix.seboolean": {
                "state": "true", 
                "name": "httpd_can_network_connect", 
                "persistent": "true"
              }
            }
          ], fp)
    sls_file = salt_convert_runner.files(path=playbook)["Converted playbooks to sls files"][0]
    with open(sls_file, "r") as fp:
        ret = yaml.safe_load(fp)

    assert ret == {'Set httpd_can_network_connect': {'selinux.boolean': [{'name': 'httpd_can_network_connect', 'persist': 'true', 'value': 'true'}]}}
