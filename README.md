# saltext-convert

Salt runner to convert other configuration management systems infrastructure as code
files to Salt states. For example, converting ansible playbook files to Salt states.

## Quickstart

To get started with your new project:

    # Create a new venv
    python3 -m venv env --prompt salt-convert
    source env/bin/activate

    # On mac, you may need to upgrade pip
    python -m pip install --upgrade pip

    # On WSL or some flavors of linux you may need to install the `enchant`
    # library in order to build the docs
    sudo apt-get install -y enchant

    # Install extension + test/dev/doc dependencies into your environment
    python -m pip install -e .[tests,dev,docs]

    # Run tests!
    python -m nox -e tests-3

    # skip requirements install for next time
    export SKIP_REQUIREMENTS_INSTALL=1

    # Build the docs, serve, and view in your web browser:
    python -m nox -e docs && (cd docs/_build/html; python -m webbrowser localhost:8000; python -m http.server; cd -)

    # Convert ansible playbooks in a given directory to SLS files
    salt-run convert.files path=/srv/ansible/
