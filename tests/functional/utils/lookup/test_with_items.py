# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=import-error
import pathlib

import pytest
import salt.runners.state as state_mod_runner
import saltext.salt_convert.runners.salt_convert as salt_convert_runner

# pylint: enable=import-error


pytestmark = [
    pytest.mark.skip_on_windows,
]


@pytest.fixture
def configure_loader_modules(minion_opts):
    opts = minion_opts.copy()

    return {
        salt_convert_runner: {
            "__opts__": opts,
        },
        state_mod_runner: {
            "__opts__": opts,
        },
    }


def test_playbook_with_items_nonsupported_list():
    """
    Test a playbook that uses with_items list
    alongside a Salt function that does
    not support a list for the name.
    """
    path = pathlib.Path(__file__).parent / "files" / "playbook-with-items-list.yml"

    sls_file = salt_convert_runner.ansible_files(path=str(path))[
        "Converted playbooks to sls files"
    ][0]

    ret = state_mod_runner.orchestrate_show_sls(
        f"ansible_convert.{pathlib.Path(sls_file).name.split('.')[0]}"
    )

    file0_state = ret["func-tests-minion-opts"]["create directory0"]["file"]
    file1_state = ret["func-tests-minion-opts"]["create directory1"]["file"]

    assert file0_state[0]["recurse"] == ["mode"]
    assert file1_state[0]["recurse"] == ["mode"]
    assert file0_state[1]["name"] == "/tmp/path1"
    assert file1_state[1]["name"] == "/tmp/path2"
    assert file0_state[2]["dir_mode"] == "0o775"
    assert file1_state[2]["dir_mode"] == "0o775"
