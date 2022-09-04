# filemanager

A script which cleans and reformats

Run in `--dry-run` mode to see what changes would be made.

Default behavior is to rename a file with the following options:

-   Remove special characters
-   Trim multiple separators (`_`, `-`, ` `)
-   Replace all `.jpeg` extensions to `.jpg`
-   Lowercase extensions
-   Avoid overwriting files by adding a unique integer

Additional options:

-   Parse the filename for a date which can be reformated as `YYYY-MM-DD` and added to the beginning of the filename, or removed
-   Normalize to a common word separator (`_`, `-`, ` `)
-   Normalize the filename to lowercase, uppercase, or titlecase

## Install

Pip

```bash
pip install git+https://github.com/natelandau/filemanager
```

[PIPX](https://pypa.github.io/pipx/)

```bash
pipx install git+https://github.com/natelandau/filemanager
```

## Usage

Run `filemanager --help` for usage

## Caveats

Built this file management application for my own personal use. It is tested on MacOS and Raspberry Pi systems. YMMV depending on your system and requirements.

## Contributing

### Setup: once per device

1. [Generate an SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) and [add the SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
1. Configure SSH to automatically load your SSH keys:
    ```sh
    cat << EOF >> ~/.ssh/config
    Host *
      AddKeysToAgent yes
      IgnoreUnknown UseKeychain
      UseKeychain yes
    EOF
    ```
1. [Install Docker Desktop](https://www.docker.com/get-started).
    - Enable _Use Docker Compose V2_ in Docker Desktop's preferences window.
    - _Linux only_:
        - [Configure Docker and Docker Compose to use the BuildKit build system](https://docs.docker.com/develop/develop-images/build_enhancements/#to-enable-buildkit-builds). On macOS and Windows, BuildKit is enabled by default in Docker Desktop.
        - Export your user's user id and group id so that [files created in the Dev Container are owned by your user](https://github.com/moby/moby/issues/3206):
            ```sh
            cat << EOF >> ~/.bashrc
            export UID=$(id --user)
            export GID=$(id --group)
            EOF
            ```
1. [Install VS Code](https://code.visualstudio.com/) and [VS Code's Remote-Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). Alternatively, install [PyCharm](https://www.jetbrains.com/pycharm/download/).
    - _Optional:_ Install a [Nerd Font](https://www.nerdfonts.com/font-downloads) such as [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode) with `brew tap homebrew/cask-fonts && brew install --cask font-fira-code-nerd-font` and [configure VS Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) or [configure PyCharm](https://github.com/tonsky/FiraCode/wiki/Intellij-products-instructions) to use `'FiraCode Nerd Font'`.

### Setup: once per project

#### Local development

1. Clone this repository.
2. Install the Poetry environment with `poetry install`.
3. Activate your Poetry environment with `poetry shell`.
4. Install the pre-commit hooks with `pre-commit install --install-hooks`.

#### Containerized development

1. Clone this repository.
2. Start a [Dev Container](https://code.visualstudio.com/docs/remote/containers) in your preferred development environment:
    - _VS Code_: open the cloned repository and run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Remote-Containers: Reopen in Container_.
    - _PyCharm_: open the cloned repository and [configure Docker Compose as a remote interpreter](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#docker-compose-remote).
    - _Terminal_: open the cloned repository and run `docker compose run --rm dev` to start an interactive Dev Container.

### Developing

-   Access an interactive terminal within the container from an external terminal application `docker compose exec -it dev /usr/bin/zsh`
-   Rebuild the `app` Docker image `docker compose build --no-cache app`
-   This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
-   Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project.
-   Run `poetry add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `poetry.lock`.
-   Run `poetry remove {package}` from within the development environment to uninstall a run time dependency and remove it from `pyproject.toml` and `poetry.lock`.
-   Run `poetry update` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`.
-   Run `cz bump` to bump the package's version, update the `CHANGELOG.md`, and create a git tag.
